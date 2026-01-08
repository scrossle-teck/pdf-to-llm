import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Reuse run_cli environment setup
from tests.test_pdf2llm_cli import run_cli, make_sample_pdf


def make_blank_pdf(path: Path, pages: int = 1) -> None:
    import fitz  # type: ignore
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page()
    doc.save(path)
    doc.close()


def test_ocr_blank_page(tmp_path: Path):
    pdf_path = tmp_path / "blank.pdf"
    out_dir = tmp_path / "out"
    make_blank_pdf(pdf_path, pages=1)

    r1 = run_cli("--out", str(out_dir), "preflight", "--pdf", str(pdf_path))
    assert r1.returncode == 0, r1.stderr
    roots = list(out_dir.glob("blank-*"))
    assert roots
    root = roots[0]

    r2 = run_cli("--out", str(out_dir), "extract", "--pdf", str(pdf_path))
    assert r2.returncode == 0, r2.stderr
    pages_dir = root / "artifacts" / "pages"
    assert pages_dir.is_dir()
    # Expect empty text for blank page
    first = json.loads((pages_dir / "00001.json").read_text(encoding="utf-8"))
    assert first.get("text", "") == ""

    # Prepare env override for tesseract if available
    env_extra = {}
    tcmd = os.environ.get("PDF2LLM_TESSERACT_CMD") or shutil.which("tesseract")
    if tcmd:
        env_extra["PDF2LLM_TESSERACT_CMD"] = tcmd
    else:
        # If no tesseract available, skip gracefully
        import pytest
        pytest.skip("tesseract not available in environment")

    r3 = run_cli("--out", str(out_dir), "ocr", "--pdf", str(pdf_path), env_extra=env_extra)
    assert r3.returncode == 0, r3.stderr
    ocr_dir = root / "artifacts" / "ocr"
    assert ocr_dir.is_dir()
    txt_path = ocr_dir / "p00001.txt"
    assert txt_path.exists(), "OCR output file should be created for blank page"
    idx = ocr_dir / "ocr.jsonl"
    assert idx.exists()
    status = json.loads((ocr_dir / "status.json").read_text(encoding="utf-8"))
    assert status.get("pages_processed", 0) >= 1
