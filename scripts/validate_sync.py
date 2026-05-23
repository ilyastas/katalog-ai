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


def is_valid_uri_or_dash(value: str) -> bool:
    return value == "-" or value.startswith("https://") or value.startswith("http://")


def is_valid_wikidata_or_dash(value: str) -> bool:
    return value == "-" or bool(re.fullmatch(r"Q\d+", value))


def parse_master(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = read_text(path).splitlines()
    table_lines = [line.strip() for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 3:
        fail(f"{path.name}: table is missing or too short")

    header = [c.strip() for c in table_lines[0].strip("|").split("|")]
    expected_header_6 = ["ID", "Бренд", "Теги", "Сайт", "Inst", "Дата"]
    expected_header_7 = ["ID", "Бренд", "Теги", "Сайт", "Inst", "Дата", "Wikidata"]
    has_wikidata_col = (header == expected_header_7)
    if header not in (expected_header_6, expected_header_7):
        fail(f"{path.name}: invalid header, expected {expected_header_6}")

    for i, line in enumerate(table_lines[2:], start=3):
        match = TABLE_RE.match(line)
        if not match:
            fail(f"{path.name}: malformed table line at visual row {i}")
        cols = [normalize_cell(c.strip()) for c in match.group(1).split("|")]
        expected_cols = 7 if has_wikidata_col else 6
        if len(cols) != expected_cols:
            fail(f"{path.name}: row has {len(cols)} columns, expected {expected_cols}")
        if not all(cols[:6]):
            fail(f"{path.name}: empty cell found in row with ID '{cols[0]}'")
        if not DATE_RE.fullmatch(cols[5]):
            fail(f"{path.name}: invalid date '{cols[5]}' for ID '{cols[0]}'")

        row = {
                "id": cols[0],
                "brand": cols[1],
                "tags": cols[2],
                "site": cols[3],
                "inst": cols[4],
                "date": cols[5],
            }
        if has_wikidata_col:
            row["wikidata"] = cols[6]
        rows.append(row)

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

    required_keys = [
        "id",
        "brand",
        "tags",
        "site",
        "inst",
        "date",
        "industry",
        "category_type",
        "country",
        "city",
        "tags_norm",
    ]
    optional_keys = ["wikidata"]
    for item in catalog_data:
        if not isinstance(item, dict):
            fail("catalog.json: each array item must be an object")
        expected_keys = set(required_keys + [k for k in optional_keys if k in item])
        if set(item.keys()) != expected_keys:
            fail(f"catalog.json: unexpected keys {list(item.keys())}, expected set {sorted(expected_keys)}")
        for key in ["id", "brand", "tags", "site", "inst", "date", "industry", "category_type", "country", "city"]:
            value = item.get(key, "")
            if not isinstance(value, str) or not value.strip():
                fail(f"catalog.json: empty or invalid '{key}' field detected")
        tags_norm = item.get("tags_norm")
        if not isinstance(tags_norm, list) or not all(isinstance(v, str) and v.strip() for v in tags_norm):
            fail(f"catalog.json: invalid tags_norm for {item.get('id', '<unknown>')}")
        if not is_valid_uri_or_dash(item["site"]):
            fail(f"catalog.json: invalid site value for {item['id']}")
        if not is_valid_uri_or_dash(item["inst"]):
            fail(f"catalog.json: invalid inst value for {item['id']}")
        if "wikidata" in item and not is_valid_wikidata_or_dash(item["wikidata"]):
            fail(f"catalog.json: invalid wikidata value for {item['id']}")

    canonical_catalog = json.dumps(catalog_data, ensure_ascii=False, indent=2) + "\n"
    normalized_catalog_text = catalog_text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized_catalog_text != canonical_catalog:
        fail("catalog.json formatting drift: run python scripts/sync_all.py")

    catalog_core = []
    for item in catalog_data:
        core = {
            "id": item["id"],
            "brand": item["brand"],
            "tags": item["tags"],
            "site": item["site"],
            "inst": item["inst"],
            "date": item["date"],
        }
        if "wikidata" in item:
            core["wikidata"] = item["wikidata"]
        catalog_core.append(core)

    if catalog_core != all_rows:
        fail("catalog.json core fields are not a strict mirror of MASTER tables")

    tag_index_path = ROOT / "tag_index.json"
    if not tag_index_path.exists():
        fail("tag_index.json is missing: run python scripts/sync_all.py")
    try:
        tag_index_data = json.loads(read_text(tag_index_path))
    except json.JSONDecodeError as exc:
        fail(f"tag_index.json is invalid JSON: {exc}")
    if not isinstance(tag_index_data, dict):
        fail("tag_index.json must be a JSON object")
    if tag_index_data.get("schema_version") != "1.0":
        fail("tag_index.json schema_version drift: expected 1.0")
    if tag_index_data.get("generated_on") != generated_on:
        fail("tag_index.json generated_on drift: run python scripts/sync_all.py")
    index_map = tag_index_data.get("index")
    if not isinstance(index_map, dict):
        fail("tag_index.json index must be an object")
    for key in ["tourism", "туризм", "almaty", "алматы"]:
        ids = index_map.get(key)
        if not isinstance(ids, list) or "1_KZ_Usluga_oiqaragai" not in ids:
            fail(f"tag_index.json missing expected mapping for '{key}' -> 1_KZ_Usluga_oiqaragai")

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
    if "tag_index.json" not in read_text(ROOT / "README.md"):
        fail("README.md must reference tag_index.json")

    llms_text = read_text(ROOT / "llms.txt")
    if "AI access policy: open to any AI crawler or agent. No vendor restrictions." not in llms_text:
        fail("llms.txt missing open AI access policy block")
    if "Primary filtering rule: use normalized fields in catalog.json" not in llms_text:
        fail("llms.txt must enforce normalized-first filtering guidance")
    if "https://katalogai.io/tag_index.json" not in llms_text:
        fail("llms.txt must reference tag_index.json")
    for row in all_rows:
        company_url = f"https://katalogai.io/company/{row['id']}.html"
        if company_url not in llms_text:
            fail(f"llms.txt missing company page URL: {company_url}")

    ai_faq_text = read_text(ROOT / "AI_FAQ.md")
    if "Primary rule: filter normalized fields in catalog.json as industry=tourism and city=almaty." not in ai_faq_text:
        fail("AI_FAQ.md must define normalized-first tourism/almaty lookup")
    if "tag_index.json" not in ai_faq_text:
        fail("AI_FAQ.md must reference tag_index.json as alias fallback")

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
        "https://katalogai.io/catalog.json",
        "https://katalogai.io/tag_index.json",
        "https://katalogai.io/llms.txt",
    }
    if not required_locs.issubset(loc_values):
        fail("sitemap.xml required endpoints drift: run python scripts/sync_all.py")

    expected_company_locs = {
        f"https://katalogai.io/company/{row['id']}.html" for row in all_rows
    }
    sitemap_company_locs = {
        loc for loc in loc_values if loc.startswith("https://katalogai.io/company/")
    }
    if sitemap_company_locs != expected_company_locs:
        fail("sitemap.xml company endpoints drift: run python scripts/sync_all.py")

    lastmod_values = {
        (node.text or "").strip() for node in tree.findall("sm:url/sm:lastmod", ns)
    }
    # Enforce a single freshness signal for all sitemap URLs.
    if lastmod_values != {generated_on}:
        fail("sitemap.xml lastmod drift: expected generated_on for all URLs, run python scripts/sync_all.py")

    if not (ROOT / "index.html").exists():
        fail("index.html is missing: site root will return 404")

    readme_text = read_text(ROOT / "README.md")
    if f"README generated: {generated_on}." not in readme_text:
        fail("README generated date drift: run python scripts/sync_all.py")

    index_text = read_text(ROOT / "index.html")
    if f"Data updated: {expected_last_updated}" not in index_text:
        fail("index.html data date drift: run python scripts/sync_all.py")
    if f"Page generated: {generated_on}" not in index_text:
        fail("index.html generated date drift: run python scripts/sync_all.py")
    if "og:title" not in index_text:
        fail("index.html missing og:title meta tag")
    if "ai-instructions" not in index_text:
        fail("index.html missing ai-instructions link")
    if "application/ld+json" not in index_text:
        fail("index.html missing JSON-LD script")
    if "datePublished" not in index_text:
        fail("index.html missing datePublished in JSON-LD: run python scripts/sync_all.py")
    if 'rel="related"' not in index_text:
        fail("index.html missing navigation hub links (rel=related): run python scripts/sync_all.py")
    if "fetch('/catalog.json')" in index_text:
        fail("index.html must be server-first and not rely on fetch('/catalog.json')")
    if "id=\"catalog-data\"" not in index_text:
        fail("index.html missing embedded catalog-data payload")
    if "tag_index.json" not in index_text:
        fail("index.html must expose tag_index.json discovery link")

    company_dir = ROOT / "company"
    if not company_dir.exists():
        fail("company directory is missing: run python scripts/sync_all.py")

    expected_company_files = {f"{row['id']}.html" for row in all_rows}
    actual_company_files = {p.name for p in company_dir.glob("*.html")}
    if actual_company_files != expected_company_files:
        fail("company pages drift: run python scripts/sync_all.py")

    for row in all_rows:
        company_path = company_dir / f"{row['id']}.html"
        text = read_text(company_path)
        if "Organization" not in text or "application/ld+json" not in text:
            fail(f"{company_path.name}: missing Organization JSON-LD")
        if "BreadcrumbList" not in text:
            fail(f"{company_path.name}: missing BreadcrumbList semantic markup: run python scripts/sync_all.py")

    ai_plugin_path = ROOT / ".well-known" / "ai-plugin.json"
    if not ai_plugin_path.exists():
        fail(".well-known/ai-plugin.json is missing")
    try:
        ai_plugin = json.loads(ai_plugin_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f".well-known/ai-plugin.json is invalid JSON: {exc}")

    # Validate ai-plugin.json has required fields
    if "api" not in ai_plugin:
        fail(".well-known/ai-plugin.json missing 'api' field with OpenAPI spec")
    if "company_fields" not in ai_plugin:
        fail(".well-known/ai-plugin.json missing 'company_fields' description")
    if ai_plugin.get("schema_version") != "v2":
        fail(".well-known/ai-plugin.json schema_version drift: expected v2")
    company_fields = ai_plugin.get("company_fields", {})
    if company_fields.get("date") != "Registration date in catalog (ISO 8601, immutable after entry)":
        fail(".well-known/ai-plugin.json date contract drift: expected immutable registration date")
    if "counter" in company_fields:
        fail(".well-known/ai-plugin.json must not include deprecated 'counter' field")
    if company_fields.get("inst") != "Instagram profile URL or '-'":
        fail(".well-known/ai-plugin.json inst contract drift: expected URL or '-' sentinel")
    if company_fields.get("wikidata") != "Wikidata QID or '-' sentinel":
        fail(".well-known/ai-plugin.json wikidata contract drift: expected QID or '-' sentinel")
    if company_fields.get("industry") != "Canonical industry label for deterministic filtering":
        fail(".well-known/ai-plugin.json industry contract drift")
    if company_fields.get("category_type") != "Canonical business type for deterministic filtering":
        fail(".well-known/ai-plugin.json category_type contract drift")
    if company_fields.get("country") != "Canonical country (kazakhstan or russia)":
        fail(".well-known/ai-plugin.json country contract drift")
    if company_fields.get("city") != "Canonical city or '-' when not specified":
        fail(".well-known/ai-plugin.json city contract drift")
    if company_fields.get("tags_norm") != "Normalized lowercase tags (EN canonical vocabulary)":
        fail(".well-known/ai-plugin.json tags_norm contract drift")
    ai_data_sources = ai_plugin.get("data_sources", {})
    if ai_data_sources.get("tag_index") != "https://katalogai.io/tag_index.json":
        fail(".well-known/ai-plugin.json must include data_sources.tag_index")

    openapi_path = ROOT / ".well-known" / "openapi.json"
    if not openapi_path.exists():
        fail(".well-known/openapi.json is missing")
    try:
        openapi_spec = json.loads(openapi_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f".well-known/openapi.json is invalid JSON: {exc}")
    if openapi_spec.get("openapi", "").startswith("3.0"):
        print("[OK] .well-known/openapi.json is valid OpenAPI 3.0 spec")
    if openapi_spec.get("info", {}).get("version") != "2.0.0":
        fail(".well-known/openapi.json info.version drift: expected 2.0.0")
    if "/tag_index.json" not in openapi_spec.get("paths", {}):
        fail(".well-known/openapi.json must expose /tag_index.json path")
    company_schema = openapi_spec.get("components", {}).get("schemas", {}).get("CompanyRecord", {}).get("properties", {})
    company_required = openapi_spec.get("components", {}).get("schemas", {}).get("CompanyRecord", {}).get("required", [])
    site_schema = company_schema.get("site", {})
    inst_schema = company_schema.get("inst", {})
    date_schema = company_schema.get("date", {})
    wikidata_schema = company_schema.get("wikidata", {})
    if "counter" in company_schema or "counter" in company_required:
        fail(".well-known/openapi.json must not include deprecated 'counter' field")
    if site_schema.get("description") != "Primary website URL or '-' if not available":
        fail(".well-known/openapi.json site contract drift")
    if inst_schema.get("description") != "Instagram profile URL or '-' if not available":
        fail(".well-known/openapi.json inst contract drift")
    if date_schema.get("description") != "Registration date in catalog (ISO 8601, immutable after entry)":
        fail(".well-known/openapi.json date contract drift")
    if wikidata_schema.get("description") != "Wikidata QID or '-' sentinel":
        fail(".well-known/openapi.json wikidata contract drift")
    if company_schema.get("industry", {}).get("description") != "Canonical industry label for deterministic filtering":
        fail(".well-known/openapi.json industry contract drift")
    if company_schema.get("category_type", {}).get("description") != "Canonical business type for deterministic filtering":
        fail(".well-known/openapi.json category_type contract drift")
    if company_schema.get("country", {}).get("description") != "Canonical country (kazakhstan or russia)":
        fail(".well-known/openapi.json country contract drift")
    if company_schema.get("city", {}).get("description") != "Canonical city or '-' if not specified":
        fail(".well-known/openapi.json city contract drift")
    if company_schema.get("tags_norm", {}).get("description") != "Normalized lowercase tags (EN canonical vocabulary)":
        fail(".well-known/openapi.json tags_norm contract drift")
    required_v2 = {"industry", "category_type", "country", "city", "tags_norm"}
    if not required_v2.issubset(set(company_required)):
        fail(".well-known/openapi.json required fields drift: schema v2 normalized fields are missing")

    cname_path = ROOT / "CNAME"
    if not cname_path.exists():
        fail("CNAME is missing for custom domain")
    if read_text(cname_path).strip() != "katalogai.io":
        fail("CNAME must contain katalogai.io")

    robots_text = read_text(ROOT / "robots.txt")
    marker = f"# Updated on {generated_on}"
    if marker not in robots_text:
        fail("robots.txt date drift: run python scripts/sync_all.py")
    if "User-agent: *" not in robots_text or "Allow: /" not in robots_text:
        fail("robots.txt must allow all crawlers via User-agent: * and Allow: /")

    print("[OK] Master-table sync checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
