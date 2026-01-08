from pathlib import Path

import fitz

from src.oneshot import oneshot


def create_sample_pdf(path: Path):
    doc = fitz.open()
    page = doc.new_page()
    # Title with larger font
    page.insert_text((72, 72), "Authentication", fontsize=20)
    page.insert_text((72, 100), "Use API keys for access.")
    page.insert_text((72, 120), "TOKEN: abc123")

    page2 = doc.new_page()
    page2.insert_text((72, 72), "Pagination", fontsize=20)
    page2.insert_text((72, 100), "Use limit and offset for paging.")

    doc.save(str(path))
    doc.close()


def test_oneshot_generates_zip_and_docs(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    create_sample_pdf(pdf_path)

    out_dir = tmp_path / "out"
    out_dir.mkdir()

    # Run oneshot by calling function via Typer-compatible signature
    oneshot.callback = None  # defensive for typer decorator
    oneshot(pdf=pdf_path, out=out_dir)

    # Subject inferred from filename
    subject = pdf_path.stem
    root = out_dir / f"{subject}-docs"

    assert (root / "README.md").exists()
    assert (root / "index.md").exists()

    # Domain directories likely created from headings
    auth_dir = root / "authentication"
    pag_dir = root / "pagination"
    assert auth_dir.exists()
    assert pag_dir.exists()

    # Files have front-matter (non-README)
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        if p.name != "README.md":
            assert text.strip().startswith("---")

    # Zip exists
    zip_path = out_dir / f"{subject}-llm-optimized-docs.zip"
    assert zip_path.exists()
