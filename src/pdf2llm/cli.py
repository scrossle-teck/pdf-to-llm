from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import typer

from .config import PipelineConfig, load_config, resolve_output_root
from .utils import sha256_file


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
    typer.echo(f"[structure] stub complete at {root}")


@app.command()
def tables(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "tables")
    typer.echo(f"[tables] stub complete at {root}")


@app.command()
def figures(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "figures")
    typer.echo(f"[figures] stub complete at {root}")


@app.command()
def ocr(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _touch_stage(root, "ocr")
    typer.echo(f"[ocr] stub complete at {root}")


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
    combined = render_dir / "combined.md"
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
    typer.echo(f"[chunk] wrote initial chunk(s) to {chunks_dir}")


@app.command()
def report(ctx: typer.Context, pdf: Path = typer.Option(..., exists=True)):
    state = ctx.obj
    cfg: PipelineConfig = state["cfg"]
    out_root = resolve_output_root(cfg, state["out"])
    root = _doc_root(out_root, pdf)
    _ensure_dir(root)
    (root / "report.md").write_text("# Report\n\nStub report.\n", encoding="utf-8")
    typer.echo(f"[report] stub complete at {root}")


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
