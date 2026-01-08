import json
import os
import subprocess
import sys
from pathlib import Path


def make_sample_pdf(path: Path, pages: int = 2) -> None:
    import fitz  # type: ignore

    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), f"Hello PDF page {i+1}")
    doc.save(path)
    doc.close()


def run_cli(*args: str, cwd: Path | None = None, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    # Ensure the src/ folder is on PYTHONPATH so `-m pdf2llm` works without install
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = str(repo_root / "src")
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    env["PYTHONPATH"] = src_dir + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run([sys.executable, "-m", "pdf2llm", *args], cwd=cwd, capture_output=True, text=True, env=env)


def test_render_fallback_no_structure(tmp_path: Path):
    pdf_path = tmp_path / "sample_no_struct.pdf"
    out_dir = tmp_path / "out"
    make_sample_pdf(pdf_path, pages=2)

    r1 = run_cli("--out", str(out_dir), "preflight", "--pdf", str(pdf_path))
    assert r1.returncode == 0, r1.stderr
    roots = list(out_dir.glob("sample_no_struct-*"))
    assert roots
    root = roots[0]
    r2 = run_cli("--out", str(out_dir), "extract", "--pdf", str(pdf_path))
    assert r2.returncode == 0, r2.stderr
    # Intentionally skip structure
    r3 = run_cli("--out", str(out_dir), "render", "--pdf", str(pdf_path))
    assert r3.returncode == 0, r3.stderr
    combined = root / "render" / "combined.md"
    s = combined.read_text(encoding="utf-8")
    assert "<!-- p:1 -->" in s
    assert "Hello PDF page 1" in s


def test_preflight_and_extract(tmp_path: Path):
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "out"
    make_sample_pdf(pdf_path, pages=3)

    r = run_cli("--out", str(out_dir), "preflight", "--pdf", str(pdf_path))
    assert r.returncode == 0, r.stderr

    # discover hashed doc root
    roots = list(out_dir.glob("sample-*"))
    assert roots, "doc root not created"
    root = roots[0]
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pages"] == 3
    assert manifest["bytes"] > 0

    r2 = run_cli("--out", str(out_dir), "extract", "--pdf", str(pdf_path))
    assert r2.returncode == 0, r2.stderr
    pages_dir = root / "artifacts" / "pages"
    assert pages_dir.is_dir()
    page_files = sorted(pages_dir.glob("*.json"))
    assert len(page_files) == 3
    first = json.loads(page_files[0].read_text(encoding="utf-8"))
    assert first["page"] == 1
    assert "Hello PDF" in first["text"]

    # structure + render
    r3 = run_cli("--out", str(out_dir), "structure", "--pdf", str(pdf_path))
    assert r3.returncode == 0, r3.stderr
    blocks = root / "artifacts" / "structure" / "blocks.jsonl"
    assert blocks.exists()

    r4 = run_cli("--out", str(out_dir), "render", "--pdf", str(pdf_path))
    assert r4.returncode == 0, r4.stderr
    combined = root / "render" / "combined.md"
    s = combined.read_text(encoding="utf-8")
    assert "<!-- p:1 -->" in s
    assert "Hello PDF page 1" in s

    # tables: should create the directory and index (may be zero tables)
    r5 = run_cli("--out", str(out_dir), "tables", "--pdf", str(pdf_path))
    assert r5.returncode == 0, r5.stderr
    tables_dir = root / "artifacts" / "tables"
    assert tables_dir.is_dir()
    idx = tables_dir / "tables.jsonl"
    assert idx.exists()

    # figures: should create the directory (may be zero images)
    r_fig = run_cli("--out", str(out_dir), "figures", "--pdf", str(pdf_path))
    assert r_fig.returncode == 0, r_fig.stderr
    figures_dir = root / "artifacts" / "figures"
    assert figures_dir.is_dir()

    # chunk: should produce a single chunk and index with page range
    r_chunk = run_cli("--out", str(out_dir), "chunk", "--pdf", str(pdf_path))
    assert r_chunk.returncode == 0, r_chunk.stderr
    chunks_dir = root / "chunks"
    assert (chunks_dir / "00001.md").exists()
    chunks_idx = chunks_dir / "chunks.jsonl"
    assert chunks_idx.exists()
    lines = [l for l in chunks_idx.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert lines, "chunks.jsonl empty"
    entry = json.loads(lines[0])
    assert entry.get("id") == "00001"
    pages_range = entry.get("pages")
    assert pages_range == [1, 3]

    # report: should summarize counts
    r_report = run_cli("--out", str(out_dir), "report", "--pdf", str(pdf_path))
    assert r_report.returncode == 0, r_report.stderr
    report_md = root / "report.md"
    assert report_md.exists()
    report_text = report_md.read_text(encoding="utf-8")
    assert "Pages (manifest): 3" in report_text
    assert "Blocks:" in report_text

    # ocr: should create the directory and a status file without requiring tesseract
    r6 = run_cli("--out", str(out_dir), "ocr", "--pdf", str(pdf_path))
    assert r6.returncode == 0, r6.stderr
    ocr_dir = root / "artifacts" / "ocr"
    assert ocr_dir.is_dir()
    status_path = ocr_dir / "status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text(encoding="utf-8"))
        assert "tesseract_in_path" in status
        assert "pytesseract_import" in status
