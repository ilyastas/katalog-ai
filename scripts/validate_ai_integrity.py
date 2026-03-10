#!/usr/bin/env python3
"""Validate AI-facing canonical data integrity and direct company profile routing."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECT_COMPANY_FILES = {
    "nrdj-salon": "NRDJ Salon",
    "secret-skin": "Secret Skin",
    "mltrade": "MLtrade",
}


def load_json(rel_path: str) -> dict:
    path = ROOT / rel_path
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing required file: {rel_path}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {rel_path}: {exc}")


def load_text(rel_path: str) -> str:
    path = ROOT / rel_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"Missing required file: {rel_path}")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_canonical_counts() -> None:
    companies_all = load_json("data/companies_all.json")
    companies_full = load_json("data/companies.json")
    anchor = load_json("AUTHORITATIVE_COMPANY_LIST.json")

    count_all = companies_all.get("count")
    count_full = companies_full.get("count")
    count_anchor = anchor.get("count")

    if count_all != count_full or count_all != count_anchor:
        fail(
            "Count mismatch across canonical files: "
            f"companies_all={count_all}, companies={count_full}, anchor={count_anchor}"
        )

    names_all = {item.get("name") for item in companies_all.get("companies", [])}
    names_full = {item.get("name") for item in companies_full.get("companies", [])}
    names_anchor = {item.get("name") for item in anchor.get("companies", [])}

    if names_all != names_full or names_all != names_anchor:
        fail("Company name sets differ across canonical files")

    print(f"OK: canonical company count={count_all}, names are synchronized")


def check_dataset_catalogs() -> None:
    index_data = load_json("data/index.json")
    root_index = load_json("index.json")

    for dataset in index_data.get("hasPart", []):
        name = dataset.get("name", "")
        url = dataset.get("url", "")
        if any(token in url for token in ["beauty.json", "museums.json", "marketplaces.json", "offers.json", "geo-index.json"]):
            fail(f"Deprecated thematic dataset still exposed in data/index.json: {url}")
        if name in {"Authoritative Company List", "Full Company Registry"} and dataset.get("authoritative") is not True:
            fail(f"Dataset '{name}' must have authoritative=true")
        if name.startswith("Company Profile:") and dataset.get("authoritative") is not False:
            fail(f"Derived dataset '{name}' must have authoritative=false")

    for dataset in root_index.get("hasPart", []):
        url = dataset.get("url", "")
        if any(token in url for token in ["beauty.json", "museums.json", "marketplaces.json", "offers.json", "geo-index.json"]):
            fail(f"Deprecated thematic dataset still exposed in index.json: {url}")

    print("OK: public catalogs expose only canonical registries and direct company profiles")


def check_direct_company_profiles() -> None:
    companies = load_json("data/companies.json")
    canonical_names = {item.get("name") for item in companies.get("companies", [])}

    for slug, expected_name in DIRECT_COMPANY_FILES.items():
        data_profile = load_json(f"data/catalog/{slug}.json")
        root_profile = load_json(f"catalog/{slug}.json")

        if data_profile.get("name") != expected_name:
            fail(f"data/catalog/{slug}.json must expose company name '{expected_name}'")
        if root_profile.get("name") != expected_name:
            fail(f"catalog/{slug}.json must expose company name '{expected_name}'")
        if expected_name not in canonical_names:
            fail(f"Direct profile '{expected_name}' is missing from canonical registry")

    for deprecated in [
        "data/catalog/beauty.json",
        "data/catalog/museums.json",
        "data/catalog/marketplaces.json",
        "data/catalog/offers.json",
        "data/catalog/geo-index.json",
        "catalog/beauty.json",
        "catalog/museums.json",
        "catalog/marketplaces.json",
        "catalog/offers.json",
        "catalog/geo-index.json",
    ]:
        if (ROOT / deprecated).exists():
            fail(f"Deprecated catalog file still exists: {deprecated}")

    print("OK: direct company profile files exist and deprecated category catalogs are removed")


def check_ai_entrypoints() -> None:
    readme = load_text("README.md")
    ai_txt = load_text("ai.txt")
    start_here = load_text("START_HERE_FOR_AI.txt")
    ai_catalog = load_json("data/ai-catalog.json")

    required_anchor = "https://ilyastas.github.io/katalog-ai/AUTHORITATIVE_COMPANY_LIST.json"

    if required_anchor not in readme:
        fail("README.md does not include AUTHORITATIVE_COMPANY_LIST.json in source list")
    if "Do not treat dataset names or section titles as companies" not in readme:
        fail("README.md is missing anti-confusion output rule")
    if "Authoritative-Company-Anchor:" not in ai_txt:
        fail("ai.txt is missing Authoritative-Company-Anchor entry")
    if "Dataset titles and category names are not company entities." not in start_here:
        fail("START_HERE_FOR_AI.txt is missing anti-confusion rule")

    direct_profiles = ai_catalog.get("direct_company_profiles", {})
    if sorted(direct_profiles.keys()) != ["mltrade", "nrdj_salon", "secret_skin"]:
        fail("data/ai-catalog.json must list exactly 3 direct company profiles")

    print("OK: AI entrypoints and ai-catalog point to direct company profiles")


def check_rag_optimization() -> None:
    catalog = load_json("data/ai-catalog.json")
    schema = load_json("data/schema.json")
    companies = load_json("data/companies.json")

    if companies.get("$schema") != "./schema.json":
        fail("companies.json must keep $schema='./schema.json'")

    for company in companies.get("companies", []):
        company_name = company.get("name", "unknown")
        keywords = company.get("keywords", [])
        if not isinstance(keywords, list) or not keywords:
            fail(f"Company '{company_name}' has empty or invalid keywords field")

    if catalog.get("title") != "KATALOG-AI: Unified Data Catalog Index":
        fail("data/ai-catalog.json is missing or invalid title")
    if schema.get("$id") != "https://ilyastas.github.io/katalog-ai/data/schema.json":
        fail("data/schema.json is missing or invalid $id reference")

    print("OK: RAG optimization files are present and keywords are populated")


def main() -> None:
    check_canonical_counts()
    check_dataset_catalogs()
    check_direct_company_profiles()
    check_ai_entrypoints()
    check_rag_optimization()
    print("PASS: AI integrity checks completed")


if __name__ == "__main__":
    main()