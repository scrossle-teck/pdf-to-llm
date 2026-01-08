from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import typer

from .config import PipelineConfig, load_config, resolve_output_root
from .utils import sha256_file
from .structure_heuristics import parse_page_text, write_blocks_jsonl


app = typer.Typer(add_completion=False, help="PDF to LLM-ready Markdown pipeline")


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _doc_root(out_root: Path, pdf_path: Path) -> Path:
    digest, size = sha256_file(pdf_path)
    return out_root / f"{pdf_path.stem}-{digest[:8]}"


def _write_manifest(root: Path, pdf: Path, size: int, digest: str) -> None:
    import json
    _ensure_dir(root)
    manifest = {
        "pdf": str(pdf),
        "bytes": size,
        "sha256": digest,
        "pages": 0,
        "stages": [],
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(None, "--config", exists=True, help="Path to pipeline config (yaml/json)"),
    out: Optional[Path] = typer.Option(None, "--out", help="Output directory root"),
):
    ctx.obj = {
        "cfg": load_config(config),
        "out": out,
    }


@app.command()
def preflight(
    ctx: typer.Context,
    pdf: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False, help="Input PDF"),
):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])

    digest, size = sha256_file(pdf)
    root = _doc_root(out_root, pdf)
    pages, meta = _pdf_basic_info(pdf)
    _write_manifest(root, pdf, size, digest)
    _update_manifest_pages(root / "manifest.json", pages, meta)
    typer.echo(f"[preflight] pages={pages} manifest at {root}")


def _touch_stage(root: Path, name: str) -> None:
    _ensure_dir(root / "artifacts" / name)


@app.command()
def extract(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "pages")
    pages_dir = root / "artifacts" / "pages"
    pages, _ = _pdf_basic_info(pdf)
    _extract_pages_text(pdf, pages_dir, pages)
    typer.echo(f"[extract] extracted {pages} pages to {pages_dir}")


# ----- internals using PyMuPDF -----

def _pdf_basic_info(pdf: Path) -> Tuple[int, dict]:
    import json
    import fitz  # type: ignore

    with fitz.open(pdf) as doc:
        pages = doc.page_count
        meta = doc.metadata or {}
    # sanitize to plain dict
    meta = {str(k): (v if isinstance(v, (int, float, str, bool)) else str(v)) for k, v in meta.items()}
    return pages, meta


def _update_manifest_pages(path: Path, pages: int, meta: dict) -> None:
    import json
    data = json.loads(path.read_text(encoding="utf-8"))
    data["pages"] = pages
    data["meta"] = meta
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _extract_pages_text(pdf: Path, out_dir: Path, pages: int) -> None:
    import json
    import fitz  # type: ignore

    _ensure_dir(out_dir)
    with fitz.open(pdf) as doc:
        for i in range(pages):
            page = doc.load_page(i)
            text = page.get_text("text")  # simple layout text
            obj = {"page": i + 1, "text": text}
            (out_dir / f"{i+1:05d}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


@app.command()
def structure(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "structure")
    pages_dir = root / "artifacts" / "pages"
    blocks_path = root / "artifacts" / "structure" / "blocks.jsonl"
    blocks = []
    if pages_dir.exists():
        for page_file in sorted(pages_dir.glob("*.json")):
            import json
            obj = json.loads(page_file.read_text(encoding="utf-8"))
            page = int(obj.get("page", 0))
            text = obj.get("text", "")
            blocks.extend(parse_page_text(page, text))
    write_blocks_jsonl(blocks, blocks_path)
    typer.echo(f"[structure] wrote {blocks_path}")


@app.command()
def tables(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "tables")
    tbl_dir = root / "artifacts" / "tables"
    _ensure_dir(tbl_dir)
    count = _extract_tables(pdf, tbl_dir)
    typer.echo(f"[tables] extracted {count} table(s) to {tbl_dir}")


@app.command()
def figures(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "figures")
    figs_dir = root / "artifacts" / "figures"
    _ensure_dir(figs_dir)
    _extract_figures(pdf, figs_dir)
    typer.echo(f"[figures] extracted images to {figs_dir}")


@app.command()
def ocr(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "ocr")
    # Write a simple availability status; do not hard-require Tesseract
    import json
    import shutil
    ocr_dir = root / "artifacts" / "ocr"
    _ensure_dir(ocr_dir)
    status = {
        "tesseract_in_path": bool(shutil.which("tesseract")),
        "pytesseract_import": False,
    }
    try:
        import pytesseract  # type: ignore  # noqa: F401
        status["pytesseract_import"] = True
    except Exception:
        status["pytesseract_import"] = False
    (ocr_dir / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    typer.echo(f"[ocr] wrote status to {ocr_dir / 'status.json'}")


@app.command()
def render(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "render")
    render_dir = root / "render"
    _ensure_dir(render_dir)
    pages_dir = root / "artifacts" / "pages"
    blocks_path = root / "artifacts" / "structure" / "blocks.jsonl"
    combined = render_dir / "combined.md"
    if blocks_path.exists():
        _render_markdown_from_blocks(blocks_path, combined)
    else:
        _render_markdown_from_pages(pages_dir, combined)
    typer.echo(f"[render] wrote {combined}")


@app.command()
def chunk(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "chunks")
    chunks_dir = root / "chunks"
    _ensure_dir(chunks_dir)
    render_md = root / "render" / "combined.md"
    if render_md.exists():
        (chunks_dir / "00001.md").write_text(render_md.read_text(encoding="utf-8"), encoding="utf-8")
        _write_chunks_index(chunks_dir, [
            {"id": "00001", "file": "00001.md", "pages": _detect_page_range(render_md)}
        ])
    typer.echo(f"[chunk] wrote initial chunk(s) to {chunks_dir}")


@app.command()
def report(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _ensure_dir(root)
    _write_report(root)
    typer.echo(f"[report] wrote {root / 'report.md'}")


@app.command()
def all(
    ctx: typer.Context,
    pdf: Path = typer.Option(..., exists=True),
):
    preflight.callback(ctx=ctx, pdf=pdf)  # type: ignore
    extract.callback(ctx=ctx, pdf=pdf)  # type: ignore
    structure.callback(ctx=ctx, pdf=pdf)  # type: ignore
    tables.callback(ctx=ctx, pdf=pdf)  # type: ignore
    figures.callback(ctx=ctx, pdf=pdf)  # type: ignore
    ocr.callback(ctx=ctx, pdf=pdf)  # type: ignore
    render.callback(ctx=ctx, pdf=pdf)  # type: ignore
    chunk.callback(ctx=ctx, pdf=pdf)  # type: ignore
    report.callback(ctx=ctx, pdf=pdf)  # type: ignore
    typer.echo("[all] pipeline stubs complete")

def _render_markdown_from_pages(pages_dir: Path, out_path: Path) -> None:
    import json
    out_lines = ["---", "title: PDF to LLM", "version: 0.1.0", "---", ""]
    if pages_dir.exists():
        for page_file in sorted(pages_dir.glob("*.json")):
            obj = json.loads(page_file.read_text(encoding="utf-8"))
            pn = obj.get("page")
            out_lines.append(f"<!-- p:{pn} -->")
            out_lines.append(obj.get("text", ""))
            out_lines.append("")
    out_path.write_text("\n".join(out_lines), encoding="utf-8")


def _render_markdown_from_blocks(blocks_path: Path, out_path: Path) -> None:
    import json
    out_lines = ["---", "title: PDF to LLM", "version: 0.1.0", "---", ""]
    with blocks_path.open("r", encoding="utf-8") as f:
        current_page = None
        for line in f:
            obj = json.loads(line)
            page = obj.get("page")
            if page != current_page:
                out_lines.append(f"<!-- p:{page} -->")
                current_page = page
            t = obj.get("type")
            text = obj.get("text", "")
            if t == "heading":
                level = int(obj.get("level", 2))
                level = min(6, max(1, level))
                out_lines.append("#" * level + " " + text)
            elif t == "list_item":
                out_lines.append(f"- {text}")
            elif t == "code":
                out_lines.append("```")
                out_lines.append(text)
                out_lines.append("```")
            else:
                out_lines.append(text)
            out_lines.append("")
    out_path.write_text("\n".join(out_lines), encoding="utf-8")


def _extract_figures(pdf: Path, out_dir: Path) -> None:
    import fitz  # type: ignore
    import hashlib
    with fitz.open(pdf) as doc:
        for i, page in enumerate(doc):
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                try:
                    if pix.n >= 5:  # CMYK or similar
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    data = pix.tobytes("png")
                finally:
                    pass
                h = hashlib.sha256(data).hexdigest()[:8]
                p = out_dir / f"p{i+1:05d}_img{img_index+1:03d}_{h}.png"
                with p.open("wb") as f:
                    f.write(data)


def _extract_tables(pdf: Path, out_dir: Path) -> int:
    import csv
    import json
    import pdfplumber  # type: ignore

    idx = out_dir / "tables.jsonl"
    n = 0
    with pdfplumber.open(str(pdf)) as doc, idx.open("w", encoding="utf-8") as index_f:
        for pi, page in enumerate(doc.pages, start=1):
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []
            for ti, rows in enumerate(tables, start=1):
                if not rows:
                    continue
                n += 1
                csv_path = out_dir / f"p{pi:05d}_t{ti:03d}.csv"
                with csv_path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for r in rows:
                        writer.writerow([c if c is not None else "" for c in r])
                index_f.write(json.dumps({
                    "page": pi,
                    "table_index": ti,
                    "file": csv_path.name,
                }) + "\n")
    return n


def _write_report(root: Path) -> None:
    import json
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8")) if (root / "manifest.json").exists() else {}
    pages_dir = root / "artifacts" / "pages"
    blocks_path = root / "artifacts" / "structure" / "blocks.jsonl"
    figs_dir = root / "artifacts" / "figures"
    num_pages = len(list(pages_dir.glob("*.json"))) if pages_dir.exists() else 0
    num_blocks = sum(1 for _ in open(blocks_path, "r", encoding="utf-8")) if blocks_path.exists() else 0
    num_figs = len(list(figs_dir.glob("*.png"))) if figs_dir.exists() else 0
    lines = [
        "# Report",
        "",
        f"PDF: {manifest.get('pdf', '')}",
        f"Pages (manifest): {manifest.get('pages', 0)}",
        f"Pages (extracted): {num_pages}",
        f"Blocks: {num_blocks}",
        f"Figures: {num_figs}",
        "",
    ]
    (root / "report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_chunks_index(chunks_dir: Path, items: list[dict]) -> None:
    import json
    (chunks_dir / "chunks.jsonl").write_text("\n".join(json.dumps(x) for x in items) + "\n", encoding="utf-8")


def _detect_page_range(md_path: Path) -> list[int]:
    # Parses <!-- p:n --> anchors to return [min, max]
    import re
    text = md_path.read_text(encoding="utf-8")
    pages = [int(m.group(1)) for m in re.finditer(r"<!--\s*p:(\d+)\s*-->", text)]
    return [min(pages), max(pages)] if pages else [1, 1]
