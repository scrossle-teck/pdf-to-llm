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


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    # Ensure the src/ folder is on PYTHONPATH so `-m pdf2llm` works without install
    repo_root = Path(__file__).resolve().parents[1]
    src_dir = str(repo_root / "src")
    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return subprocess.run([sys.executable, "-m", "pdf2llm", *args], cwd=cwd, capture_output=True, text=True, env=env)


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
