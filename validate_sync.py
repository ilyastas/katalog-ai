#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MASTER_FILES = [ROOT / "MASTER_KZ.md", ROOT / "MASTER_RU.md"]
TABLE_RE = re.compile(r"^\|(.+)\|$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing file: {path.name}")
    return path.read_text(encoding="utf-8")


def normalize_cell(value: str) -> str:
    # Markdown autolinks may be represented as <https://example.com>.
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1].strip()
    return value


def parse_master(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = read_text(path).splitlines()
    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 3:
        fail(f"{path.name}: table is missing or too short")

    header = [c.strip() for c in table_lines[0].strip("|").split("|")]
    expected_header = ["ID", "Бренд", "Теги", "Сайт", "Inst", "Дата"]
    if header != expected_header:
        fail(f"{path.name}: invalid header, expected {expected_header}")

    for i, line in enumerate(table_lines[2:], start=3):
        match = TABLE_RE.match(line)
        if not match:
            fail(f"{path.name}: malformed table line at visual row {i}")
        cols = [normalize_cell(c.strip()) for c in match.group(1).split("|")]
        if len(cols) != 6:
            fail(f"{path.name}: row has {len(cols)} columns, expected 6")
        if not all(cols):
            fail(f"{path.name}: empty cell found in row with ID '{cols[0]}'")
        if not DATE_RE.fullmatch(cols[5]):
            fail(f"{path.name}: invalid date '{cols[5]}' for ID '{cols[0]}'")

        rows.append(
            {
                "id": cols[0],
                "brand": cols[1],
                "tags": cols[2],
                "site": cols[3],
                "inst": cols[4],
                "date": cols[5],
            }
        )

    if not rows:
        fail(f"{path.name}: no data rows found")
    return rows


def main() -> int:
    all_rows: list[dict[str, str]] = []
    for master in MASTER_FILES:
        all_rows.extend(parse_master(master))

    catalog_path = ROOT / "catalog.json"
    catalog_data = json.loads(read_text(catalog_path))
    if not isinstance(catalog_data, list):
        fail("catalog.json must be a JSON array")

    if catalog_data != all_rows:
        fail("catalog.json is not a strict mirror of MASTER tables")

    expected_files = ["MASTER_KZ.md", "MASTER_RU.md"]
    for name in ["README.md", "llms.txt"]:
        text = read_text(ROOT / name)
        for expected in expected_files:
            if expected not in text:
                fail(f"{name}: missing link or reference to {expected}")

    print("[OK] Master-table sync checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
