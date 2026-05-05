#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Set


ROOT = Path(__file__).resolve().parent.parent
CARD_RE = re.compile(r"\d+_[A-Z]{2}_[A-Za-z]+_[^\s\)\"'<>]+\.md")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing file: {path.name}")
    return path.read_text(encoding="utf-8")


def extract_cards(path: Path) -> Set[str]:
    text = read_text(path)
    return set(CARD_RE.findall(text))


def require_date_in_line(path: Path, marker: str, expected_date: str) -> None:
    text = read_text(path)
    for line in text.splitlines():
        if marker in line:
            if expected_date not in line:
                fail(f"{path.name}: expected date {expected_date} in line with '{marker}'")
            return
    fail(f"{path.name}: missing marker '{marker}'")


def main() -> int:
    catalog_path = ROOT / "catalog.json"
    catalog = json.loads(read_text(catalog_path))

    expected_date = catalog.get("metadata", {}).get("last_updated")
    if not expected_date or not DATE_RE.fullmatch(expected_date):
        fail("catalog.json: metadata.last_updated is missing or invalid")

    file_paths = [item.get("file_path", "") for item in catalog.get("index", [])]
    if not file_paths:
        fail("catalog.json: index is empty")

    catalog_cards = set(file_paths)
    if "" in catalog_cards:
        fail("catalog.json: empty file_path found")

    # 1) All catalog card files must exist and be zero-byte
    for rel in sorted(catalog_cards):
        path = ROOT / rel
        if not path.exists():
            fail(f"card file does not exist: {rel}")
        if path.stat().st_size != 0:
            fail(f"card file must be 0 bytes: {rel}")

    # 2) Cross-file card set consistency
    files_to_check = [
        ROOT / "README.md",
        ROOT / "llms.txt",
        ROOT / "ai.txt",
        ROOT / "index.html",
        ROOT / "sitemap.xml",
    ]
    for f in files_to_check:
        found = extract_cards(f)
        if found != catalog_cards:
            missing = sorted(catalog_cards - found)
            extra = sorted(found - catalog_cards)
            fail(
                f"{f.name}: card set mismatch; "
                f"missing={missing if missing else '[]'}, "
                f"extra={extra if extra else '[]'}"
            )

    # 3) Date markers consistency
    require_date_in_line(ROOT / "README.md", "Last updated:", expected_date)
    require_date_in_line(ROOT / "llms.txt", "Last updated:", expected_date)
    require_date_in_line(ROOT / "index.html", "Last updated:", expected_date)
    require_date_in_line(ROOT / "robots.txt", "Updated on", expected_date)

    # 4) All sitemap lastmod entries must match expected_date
    sitemap = read_text(ROOT / "sitemap.xml")
    lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap)
    if not lastmods:
        fail("sitemap.xml: no <lastmod> entries found")
    bad = sorted({value for value in lastmods if value != expected_date})
    if bad:
        fail(f"sitemap.xml: lastmod values must be {expected_date}, found {bad}")

    print("[OK] Katalog sync checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
