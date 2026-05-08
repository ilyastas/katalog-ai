#!/usr/bin/env python3
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MASTER_FILES = [ROOT / "MASTER_KZ.md", ROOT / "MASTER_RU.md"]
TABLE_RE = re.compile(r"^\|(.+)\|$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
COUNTER_RE = re.compile(r"\d{3}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing file: {path.name}")
    return path.read_text(encoding="utf-8")


def read_bytes(path: Path) -> bytes:
    if not path.exists():
        fail(f"Missing file: {path.name}")
    return path.read_bytes()


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
    expected_header = ["ID", "Бренд", "Теги", "Сайт", "Inst", "Дата", "COUNTER"]
    if header != expected_header:
        fail(f"{path.name}: invalid header, expected {expected_header}")

    for i, line in enumerate(table_lines[2:], start=3):
        match = TABLE_RE.match(line)
        if not match:
            fail(f"{path.name}: malformed table line at visual row {i}")
        cols = [normalize_cell(c.strip()) for c in match.group(1).split("|")]
        if len(cols) != 7:
            fail(f"{path.name}: row has {len(cols)} columns, expected 7")
        if not all(cols):
            fail(f"{path.name}: empty cell found in row with ID '{cols[0]}'")
        if not DATE_RE.fullmatch(cols[5]):
            fail(f"{path.name}: invalid date '{cols[5]}' for ID '{cols[0]}'")
        if not COUNTER_RE.fullmatch(cols[6]):
            fail(f"{path.name}: invalid COUNTER '{cols[6]}' for ID '{cols[0]}'")

        rows.append(
            {
                "id": cols[0],
                "brand": cols[1],
                "tags": cols[2],
                "site": cols[3],
                "inst": cols[4],
                "date": cols[5],
                "counter": cols[6],
            }
        )

    if not rows:
        fail(f"{path.name}: no data rows found")
    return rows


def main() -> int:
    all_rows: list[dict[str, str]] = []
    for master in MASTER_FILES:
        all_rows.extend(parse_master(master))
    expected_last_updated = max(row["date"] for row in all_rows)
    generated_on = date.today().isoformat()

    catalog_path = ROOT / "catalog.json"
    catalog_bytes = read_bytes(catalog_path)
    if catalog_bytes.startswith(b"\xef\xbb\xbf"):
        fail("catalog.json must be UTF-8 without BOM")

    catalog_text = catalog_bytes.decode("utf-8")
    catalog_data = json.loads(catalog_text)
    if not isinstance(catalog_data, list):
        fail("catalog.json must be a JSON array")

    required_keys = ["id", "brand", "tags", "site", "inst", "date", "counter"]
    for item in catalog_data:
        if not isinstance(item, dict):
            fail("catalog.json: each array item must be an object")
        if list(item.keys()) != required_keys:
            fail("catalog.json: keys must be exactly [id, brand, tags, site, inst, date, counter]")
        for key in required_keys:
            value = item.get(key, "")
            if not isinstance(value, str) or not value.strip():
                fail(f"catalog.json: empty or invalid '{key}' field detected")

    canonical_catalog = json.dumps(catalog_data, ensure_ascii=False, indent=2) + "\n"
    normalized_catalog_text = catalog_text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized_catalog_text != canonical_catalog:
        fail("catalog.json formatting drift: run python scripts/sync_all.py")

    if catalog_data != all_rows:
        fail("catalog.json is not a strict mirror of MASTER tables")

    expected_files = [
        "MASTER_KZ.md",
        "MASTER_RU.md",
        "AI_METHOD.md",
        "AI_SCHEMA.md",
        "AI_FAQ.md",
    ]
    for name in ["README.md", "llms.txt"]:
        text = read_text(ROOT / name)
        for expected in expected_files:
            if expected not in text:
                fail(f"{name}: missing link or reference to {expected}")

    for semantic_doc in ["AI_METHOD.md", "AI_SCHEMA.md", "AI_FAQ.md"]:
        if not (ROOT / semantic_doc).exists():
            fail(f"{semantic_doc} is missing: run python scripts/sync_all.py")

    # Ensure sitemap keeps the required endpoints for crawlers.
    sitemap_path = ROOT / "sitemap.xml"
    tree = ET.fromstring(read_text(sitemap_path))
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc_values = {
        (node.text or "").strip() for node in tree.findall("sm:url/sm:loc", ns)
    }
    required_locs = {
        "https://katalogai.io/",
        "https://katalogai.io/llms.txt",
        "https://katalogai.io/catalog.json",
        "https://katalogai.io/MASTER_KZ.md",
        "https://katalogai.io/MASTER_RU.md",
        "https://katalogai.io/README.md",
        "https://katalogai.io/AI_METHOD.md",
        "https://katalogai.io/AI_SCHEMA.md",
        "https://katalogai.io/AI_FAQ.md",
    }
    if loc_values != required_locs:
        fail("sitemap.xml entries drift: run python scripts/sync_all.py")

    lastmod_values = {
        (node.text or "").strip() for node in tree.findall("sm:url/sm:lastmod", ns)
    }
    if lastmod_values != {generated_on}:
        fail(f"sitemap.xml lastmod drift: expected {generated_on}, run python scripts/sync_all.py")

    if not (ROOT / "index.html").exists():
        fail("index.html is missing: GitHub Pages root will return 404")

    index_text = read_text(ROOT / "index.html")
    if f"Data updated: {expected_last_updated}" not in index_text:
        fail("index.html data date drift: run python scripts/sync_all.py")
    if "og:title" not in index_text:
        fail("index.html missing og:title meta tag")
    if "ai-instructions" not in index_text:
        fail("index.html missing ai-instructions link")
    if "application/ld+json" not in index_text:
        fail("index.html missing JSON-LD script")

    ai_plugin_path = ROOT / ".well-known" / "ai-plugin.json"
    if not ai_plugin_path.exists():
        fail(".well-known/ai-plugin.json is missing")
    try:
        json.loads(ai_plugin_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f".well-known/ai-plugin.json is invalid JSON: {exc}")

    cname_path = ROOT / "CNAME"
    if not cname_path.exists():
        fail("CNAME is missing for custom domain")
    if read_text(cname_path).strip() != "katalogai.io":
        fail("CNAME must contain katalogai.io")

    robots_text = read_text(ROOT / "robots.txt")
    marker = f"# Updated on {generated_on}"
    if marker not in robots_text:
        fail("robots.txt date drift: run python scripts/sync_all.py")

    print("[OK] Master-table sync checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
