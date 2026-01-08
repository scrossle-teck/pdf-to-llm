import csv
import json
from pathlib import Path
from typing import Dict, Any


def _count_files(root: Path, pattern: str) -> int:
    return len(list(root.glob(pattern)))


def _read_tables_index(index_path: Path) -> Dict[str, Any]:
    entries = []
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines to keep report resilient
                    continue
    return {"entries": entries, "count": len(entries)}


def _count_table_rows(tables_dir: Path) -> int:
    total = 0
    for csv_path in tables_dir.glob("*.csv"):
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            # Exclude header if present by requiring at least one row
            if len(rows) > 1:
                total += len(rows) - 1
            elif len(rows) == 1:
                # Treat single row as data if no header convention is known
                total += 1
    return total


def generate_report(output_root: str) -> str:
    root = Path(output_root)
    ocr_dir = root / "ocr"
    tables_dir = root / "tables"
    figures_dir = root / "figures"

    ocr_count = _count_files(ocr_dir, "p*.txt")
    figures_count = _count_files(figures_dir, "*.png")

    tables_index = _read_tables_index(tables_dir / "tables.jsonl")
    tables_count = _count_files(tables_dir, "*.csv")
    table_rows = _count_table_rows(tables_dir)

    report_md = root / "report.md"
    lines = [
        "# Pipeline Report",
        "",
        f"OCR: {ocr_count}",
        f"Tables: {tables_count}",
        f"Table Rows: {table_rows}",
        f"Figures: {figures_count}",
        "",
        "## Tables Index",
        f"Entries: {tables_index['count']}",
    ]
    if tables_index["entries"]:
        lines.append("")
        lines.append("### Entries")
        for i, e in enumerate(tables_index["entries"], start=1):
            csv_rel = e.get("csv") or e.get("path") or "(unknown)"
            lines.append(f"- {i}. {csv_rel}")

    report_md.write_text("\n".join(lines), encoding="utf-8")
    return str(report_md)
