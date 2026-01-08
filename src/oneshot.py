import io
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

import fitz  # PyMuPDF
import typer


app = typer.Typer(help="ONE-SHOT PDF→LLM optimized documentation converter")


@dataclass
class Unit:
    domain: str
    title: str
    body: str
    section: Optional[str] = None


def infer_subject(pdf_path: Path, doc: fitz.Document) -> str:
    meta_title = doc.metadata.get("title") or ""
    if meta_title:
        subject = re.sub(r"\s+", " ", meta_title).strip()
    else:
        subject = pdf_path.stem
    # Normalize to filesystem-friendly
    subject = re.sub(r"[^A-Za-z0-9._-]+", "-", subject).strip("-")
    return subject or "subject"


def extract_units(pdf_path: Path) -> List[Unit]:
    doc = fitz.open(str(pdf_path))
    units: List[Unit] = []
    current_domain = "general"
    current_title = "Introduction"
    current_body_lines: List[str] = []

    def flush_unit():
        nonlocal current_title, current_domain, current_body_lines
        if current_body_lines:
            units.append(Unit(domain=current_domain, title=current_title, body="\n".join(current_body_lines)))
            current_body_lines = []

    for page in doc:
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                # Heuristic: heading if any span has size >= 16
                max_size = max((span.get("size", 0) for span in line.get("spans", [])), default=0)
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                clean = line_text.strip()
                if not clean:
                    continue
                if max_size >= 16 or (clean.isupper() and len(clean) > 6):
                    # Heading encountered: decide domain and title
                    flush_unit()
                    # Domain inferred from first word group
                    domain_candidate = re.split(r"\s+", clean)[0]
                    domain_candidate = re.sub(r"[^A-Za-z0-9._-]", "", domain_candidate).lower() or "general"
                    current_domain = domain_candidate
                    current_title = clean
                else:
                    current_body_lines.append(clean)
        current_body_lines.append("")

    flush_unit()
    if not units:
        # Fallback: entire document is one unit
        full_text = "\n".join(page.get_text() for page in doc)
        units.append(Unit(domain="general", title="Document", body=full_text))
    doc.close()
    return units


def yaml_front_matter(subject: str, unit: Unit, unit_type: str = "reference") -> str:
    fm = {
        "title": unit.title,
        "type": unit_type,
        "product": subject,
        "vendor": None,
        "language": None,
        "domain": unit.domain,
        "llm_use": "reference",
        "prerequisites": [],
        "inputs": "none",
        "outputs": "none",
        "state_effect": "none",
        "tags": [],
        "source": {"type": "pdf", "title": subject, "section": unit.section or unit.title},
    }
    # Remove None fields for cleanliness
    def prune(d: Dict):
        return {k: v for k, v in d.items() if v is not None}
    fm["source"] = prune(fm["source"])  # type: ignore
    return "---\n" + "\n".join(
        [
            f"title: {fm['title']}",
            f"type: {fm['type']}",
            f"product: {fm['product']}",
            *( [f"vendor: {fm['vendor']}"] if fm.get("vendor") else [] ),
            *( [f"language: {fm['language']}"] if fm.get("language") else [] ),
            f"domain: {fm['domain']}",
            f"llm_use: {fm['llm_use']}",
            "prerequisites:",
            *( ["  - "] if not fm.get("prerequisites") else [*(f"  - {p}" for p in fm["prerequisites"]) ] ),
            f"inputs: {fm.get('inputs', 'none')}",
            f"outputs: {fm.get('outputs', 'none')}",
            f"state_effect: {fm['state_effect']}",
            "tags:",
            *( ["  - "] if not fm.get("tags") else [*(f"  - {t}" for t in fm["tags"]) ] ),
            "source:",
            *(f"  {k}: {v}" for k, v in fm["source"].items()),
            "---",
        ]
    )


def write_readme(root: Path, subject: str):
    content = "\n".join(
        [
            "# README",
            "",
            f"This package contains LLM-optimized documentation extracted from the authoritative PDF: {subject}.",
            "Files are split into atomic units with YAML front-matter elsewhere, and an index.md for navigation.",
            "Do not modify structure; use index.md and domain directories for navigation.",
        ]
    )
    (root / "README.md").write_text(content, encoding="utf-8")


def write_index(root: Path, subject: str, units: List[Unit]):
    domains: Dict[str, List[Unit]] = {}
    for u in units:
        domains.setdefault(u.domain, []).append(u)
    fm = "\n".join(
        [
            "---",
            f"title: index",
            f"type: index",
            f"product: {subject}",
            "llm_use: reference",
            "source:",
            f"  type: pdf",
            f"  title: {subject}",
            "---",
        ]
    )
    lines = [fm, "", "# Index", ""]
    for d, items in domains.items():
        lines.append(f"## {d}")
        for u in items:
            filename = make_filename(u.title)
            lines.append(f"- {u.title} — {d}/{filename}.md")
        lines.append("")
    (root / "index.md").write_text("\n".join(lines), encoding="utf-8")


def make_filename(title: str) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", title.strip()).strip("-")
    return base[:80] or "unit"


def normalize_common_concepts(root: Path, units: List[Unit]):
    # Simple de-dup: find paragraphs appearing 5+ times and extract
    para_freq: Dict[str, int] = {}
    for u in units:
        for para in [p.strip() for p in u.body.split("\n\n") if p.strip()]:
            para_freq[para] = para_freq.get(para, 0) + 1
    common = [p for p, c in para_freq.items() if c >= 5]
    if not common:
        return
    shared_dir = root / "shared"
    shared_dir.mkdir(parents=True, exist_ok=True)
    common_md = shared_dir / "common-concepts.md"
    fm = "\n".join(["---", "title: common-concepts", "type: concept", "llm_use: reference", "---"])  # minimal
    body = "\n\n".join(common)
    common_md.write_text(fm + "\n\n# Common Concepts\n\n" + body, encoding="utf-8")
    # Remove from units
    for u in units:
        for para in common:
            u.body = u.body.replace(para + "\n\n", "")


def write_units(root: Path, subject: str, units: List[Unit]):
    for u in units:
        domain_dir = root / u.domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        filename = make_filename(u.title) + ".md"
        fm = yaml_front_matter(subject, u, unit_type="reference")
        body_sections = [
            f"# {u.title}",
            "",
            "## Purpose",
            "",
            "## Prerequisites",
            "",
            "## Syntax",
            "```text",
            u.body,
            "```",
            "",
            "## Parameters / Inputs",
            "",
            "## Output / Response",
            "",
            "## Examples",
            "```text",
            u.body,
            "```",
            "",
            "## Notes",
            "",
        ]
        content = fm + "\n\n" + "\n".join(body_sections)
        (domain_dir / filename).write_text(content, encoding="utf-8")


def validate_package(root: Path):
    # Basic checks per spec
    assert (root / "README.md").exists(), "README.md missing"
    assert (root / "index.md").exists(), "index.md missing"
    for p in root.rglob("*.md"):
        if p.name == "README.md":
            text = p.read_text(encoding="utf-8")
            assert not text.strip().startswith("---"), "README.md must not have front-matter"
        else:
            text = p.read_text(encoding="utf-8")
            assert text.strip().startswith("---"), f"Front-matter missing in {p}"


def package_zip(root: Path, subject: str, out_zip_dir: Path):
    zip_name = f"{subject}-llm-optimized-docs.zip"
    zip_path = out_zip_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in root.rglob("*"):
            if p.is_file():
                arcname = str(p.relative_to(root.parent))
                zf.write(p, arcname=arcname)
    return zip_path


@app.command()
def oneshot(pdf: Path, out: Path = Path("out")):
    """Run the ONE-SHOT conversion: PDF → spec-compliant docs → ZIP."""
    doc = fitz.open(str(pdf))
    subject = infer_subject(pdf, doc)
    doc.close()
    root = out / f"{subject}-docs"
    root.mkdir(parents=True, exist_ok=True)

    units = extract_units(pdf)
    write_readme(root, subject)
    write_units(root, subject, units)
    write_index(root, subject, units)
    normalize_common_concepts(root, units)

    validate_package(root)
    zip_path = package_zip(root, subject, out)
    typer.echo(f"Created: {zip_path}")


if __name__ == "__main__":
    app()
