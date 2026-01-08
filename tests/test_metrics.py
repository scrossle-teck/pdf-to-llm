import json
import os
from pathlib import Path

from tests.test_pdf2llm_cli import run_cli, make_sample_pdf


def test_stage_metrics_written(tmp_path: Path):
    pdf_path = tmp_path / "m.pdf"
    out_dir = tmp_path / "out"
    make_sample_pdf(pdf_path, pages=1)

    r1 = run_cli("--out", str(out_dir), "preflight", "--pdf", str(pdf_path))
    assert r1.returncode == 0, r1.stderr
    roots = list(out_dir.glob("m-*"))
    assert roots
    root = roots[0]

    r2 = run_cli("--out", str(out_dir), "extract", "--pdf", str(pdf_path))
    assert r2.returncode == 0, r2.stderr

    r3 = run_cli("--out", str(out_dir), "structure", "--pdf", str(pdf_path))
    assert r3.returncode == 0, r3.stderr
    metrics_dir = root / "artifacts" / "metrics"
    assert metrics_dir.is_dir()
    sfile = metrics_dir / "structure.json"
    assert sfile.exists()
    s = json.loads(sfile.read_text(encoding="utf-8"))
    assert s.get("stage") == "structure"
    assert s.get("engine") == "heuristic"

    r4 = run_cli("--out", str(out_dir), "tables", "--pdf", str(pdf_path))
    assert r4.returncode == 0, r4.stderr
    tfile = metrics_dir / "tables.json"
    assert tfile.exists()
    t = json.loads(tfile.read_text(encoding="utf-8"))
    assert t.get("stage") == "tables"
    assert t.get("engine") == "heuristic"
