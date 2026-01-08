import json
from pathlib import Path

from src.report import generate_report


def write_csv(path: Path, rows):
    path.write_text("\n".join(",".join(map(str, r)) for r in rows), encoding="utf-8")


def test_report_counts_and_tables_index(tmp_path):
    root = tmp_path / "out-root"
    (root / "ocr").mkdir(parents=True)
    (root / "tables").mkdir(parents=True)
    (root / "figures").mkdir(parents=True)

    # Fake OCR files
    for i in range(1, 3):
        (root / "ocr" / f"p{i:05d}.txt").write_text("sample ocr text", encoding="utf-8")

    # Fake figures
    for i in range(1, 4):
        (root / "figures" / f"fig_{i}.png").write_bytes(b"PNG")

    # Tables CSVs
    t1 = root / "tables" / "t0001.csv"
    t2 = root / "tables" / "t0002.csv"
    write_csv(t1, [["col1", "col2"], ["a", "b"], ["c", "d"]])
    write_csv(t2, [["col1", "col2"], ["e", "f"]])

    # tables.jsonl index
    index = root / "tables" / "tables.jsonl"
    entries = [
        {"csv": "tables/t0001.csv", "page": 1},
        {"csv": "tables/t0002.csv", "page": 2},
    ]
    index.write_text("\n".join(json.dumps(e) for e in entries), encoding="utf-8")

    report_path = generate_report(str(root))
    content = Path(report_path).read_text(encoding="utf-8")

    assert "OCR: 2" in content
    assert "Figures: 3" in content
    assert "Tables: 2" in content
    # t0001 has 2 data rows, t0002 has 1 data row => total 3
    assert "Table Rows: 3" in content
    assert "Entries: 2" in content


def test_tables_index_and_csv_consistency(tmp_path):
    root = tmp_path / "out-root"
    (root / "tables").mkdir(parents=True)

    t1 = root / "tables" / "t0001.csv"
    t2 = root / "tables" / "t0002.csv"
    write_csv(t1, [["h1", "h2"], [1, 2]])
    write_csv(t2, [["h1", "h2"], [3, 4]])

    entries = [
        {"csv": "tables/t0001.csv"},
        {"csv": "tables/t0002.csv"},
    ]
    (root / "tables" / "tables.jsonl").write_text(
        "\n".join(json.dumps(e) for e in entries), encoding="utf-8"
    )

    # Generate report and then ensure all CSVs in index exist
    report_path = generate_report(str(root))
    assert Path(report_path).exists()

    # Validate CSV existence from index entries
    index_content = (root / "tables" / "tables.jsonl").read_text(encoding="utf-8").splitlines()
    for line in index_content:
        e = json.loads(line)
        csv_rel = e.get("csv")
        assert csv_rel, "Index entry must contain 'csv' path"
        csv_path = root / Path(csv_rel)
        assert csv_path.exists(), f"Missing CSV referenced by index: {csv_rel}"
