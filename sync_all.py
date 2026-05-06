#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Final


ROOT: Final[Path] = Path(__file__).resolve().parent
MASTER_FILES: Final[list[Path]] = [ROOT / "MASTER_KZ.md", ROOT / "MASTER_RU.md"]
TABLE_RE: Final[re.Pattern[str]] = re.compile(r"^\|(.+)\|$")
DATE_RE: Final[re.Pattern[str]] = re.compile(r"\d{4}-\d{2}-\d{2}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"Missing file: {path.name}")
    return path.read_text(encoding="utf-8")


def normalize_cell(value: str) -> str:
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


def write_text(path: Path, content: str) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def build_readme(last_updated: str) -> str:
    return (
        "# Katalog-AI: Master-Table Architecture\n\n"
        f"Last updated: {last_updated}.\n\n"
        "Репозиторий переведен в формат единого организма:\n\n"
        "- Источник истины для контента: таблицы в `MASTER_KZ.md` и `MASTER_RU.md`\n"
        "- Машиночитаемое зеркало: `catalog.json`\n\n"
        "## Master-файлы\n\n"
        "- [MASTER_KZ.md](MASTER_KZ.md)\n"
        "- [MASTER_RU.md](MASTER_RU.md)\n\n"
        "## Автосинхронизация\n\n"
        "- После изменений в MASTER-таблицах запусти `python sync_all.py`.\n"
        "- Скрипт обновляет `catalog.json`, `README.md`, `llms.txt`, `sitemap.xml`.\n"
        "- Перед коммитом обязательно запусти `python validate_sync.py`.\n\n"
        "## Инфраструктура\n\n"
        "- [catalog.json](catalog.json)\n"
        "- [llms.txt](llms.txt)\n"
        "- [Schema](.infra/docs/SCHEMA.md)\n"
        "- [Sync Protocol](.infra/docs/SYNC_PROTOCOL.md)\n"
        "- [Contributing](.infra/docs/CONTRIBUTING.md)\n"
        "- [robots.txt](robots.txt)\n"
        "- [sitemap.xml](sitemap.xml)\n"
    )


def build_llms(last_updated: str) -> str:
    return (
        "# Katalog-AI LLM Index\n\n"
        f"Last updated: {last_updated}\n\n"
        "Single source of truth is stored in regional master tables.\n\n"
        "## Files\n\n"
        "- [Catalog JSON Index](catalog.json)\n"
        "- [Master KZ Companies](MASTER_KZ.md)\n"
        "- [Master RU Companies](MASTER_RU.md)\n"
    )


def build_sitemap(last_updated: str) -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        "  <url>\n"
        "    <loc>https://katalogai.io/llms.txt</loc>\n"
        f"    <lastmod>{last_updated}</lastmod>\n"
        "  </url>\n"
        "  <url>\n"
        "    <loc>https://katalogai.io/catalog.json</loc>\n"
        f"    <lastmod>{last_updated}</lastmod>\n"
        "  </url>\n"
        "  <url>\n"
        "    <loc>https://katalogai.io/MASTER_KZ.md</loc>\n"
        f"    <lastmod>{last_updated}</lastmod>\n"
        "  </url>\n"
        "  <url>\n"
        "    <loc>https://katalogai.io/MASTER_RU.md</loc>\n"
        f"    <lastmod>{last_updated}</lastmod>\n"
        "  </url>\n"
        "</urlset>\n"
    )


def build_robots(last_updated: str) -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Allow: /README.md\n"
        "Disallow: /venv/\n"
        "Disallow: /.venv/\n"
        "Disallow: /.infra/\n\n"
        "# Priority for AI-crawlers\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "User-agent: ChatGPT-User\n"
        "Allow: /\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "User-agent: anthropic-ai\n"
        "Allow: /\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n\n"
        "Sitemap: https://katalogai.io/sitemap.xml\n\n"
        f"# Updated on {last_updated}\n"
    )


def main() -> int:
    all_rows: list[dict[str, str]] = []
    for master in MASTER_FILES:
        all_rows.extend(parse_master(master))

    last_updated = max(row["date"] for row in all_rows)

    changed: list[str] = []

    catalog_content = json.dumps(all_rows, ensure_ascii=False, indent=2) + "\n"
    if write_text(ROOT / "catalog.json", catalog_content):
        changed.append("catalog.json")

    if write_text(ROOT / "README.md", build_readme(last_updated)):
        changed.append("README.md")

    if write_text(ROOT / "llms.txt", build_llms(last_updated)):
        changed.append("llms.txt")

    if write_text(ROOT / "sitemap.xml", build_sitemap(last_updated)):
        changed.append("sitemap.xml")

    if write_text(ROOT / "robots.txt", build_robots(last_updated)):
        changed.append("robots.txt")

    if changed:
        print(f"[OK] Updated: {', '.join(changed)}")
    else:
        print("[OK] No changes needed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
