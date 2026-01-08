import os
import sys
import json
from pathlib import Path

from tests.test_pdf2llm_cli import run_cli


def test_figures_extraction_with_embedded_image(tmp_path: Path):
    from PIL import Image
    import fitz  # type: ignore

    # Create a small image and save
    img_path = tmp_path / "img.png"
    im = Image.new("RGB", (64, 64), color=(255, 0, 0))
    im.save(img_path)

    # Create PDF and insert image
    pdf_path = tmp_path / "with_image.pdf"
    doc = fitz.open()
    page = doc.new_page(width=200, height=200)
    rect = fitz.Rect(50, 50, 150, 150)
    page.insert_image(rect, filename=str(img_path))
    doc.save(pdf_path)
    doc.close()

    out_dir = tmp_path / "out"
    r1 = run_cli("--out", str(out_dir), "preflight", "--pdf", str(pdf_path))
    assert r1.returncode == 0, r1.stderr
    roots = list(out_dir.glob("with_image-*"))
    assert roots
    root = roots[0]

    r2 = run_cli("--out", str(out_dir), "figures", "--pdf", str(pdf_path))
    assert r2.returncode == 0, r2.stderr
    figures_dir = root / "artifacts" / "figures"
    assert figures_dir.is_dir()
    pngs = list(figures_dir.glob("*.png"))
    assert len(pngs) >= 1, "Expected at least one extracted image"
