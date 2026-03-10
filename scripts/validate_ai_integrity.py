#!/usr/bin/env python3
"""Validate AI-facing canonical data integrity and anti-confusion rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    if None in names_all:
        fail("One or more canonical company entries miss the 'name' field")

    print(f"OK: canonical company count={count_all}, names are synchronized")


def check_dataset_title_confusion() -> None:
    companies_all = load_json("data/companies_all.json")
    index_data = load_json("data/index.json")

    company_names = {item.get("name") for item in companies_all.get("companies", [])}
    dataset_titles = {
        item.get("name")
        for item in index_data.get("hasPart", [])
        if isinstance(item, dict) and item.get("name")
    }

    overlap = sorted(company_names.intersection(dataset_titles))
    if overlap:
        fail(f"Dataset titles collide with canonical company names: {', '.join(overlap)}")

    for item in index_data.get("hasPart", []):
        if not isinstance(item, dict):
            continue
        name = item.get("name", "")
        if name in {"Authoritative Company List", "Full Company Registry"}:
            if item.get("authoritative") is not True:
                fail(f"Dataset '{name}' must have authoritative=true")
        else:
            if item.get("authoritative") is not False:
                fail(f"Dataset '{name}' must have authoritative=false")

    print("OK: dataset titles are separated from canonical company entities")


def check_ai_entrypoints() -> None:
    readme = load_text("README.md")
    ai_txt = load_text("ai.txt")
    start_here = load_text("START_HERE_FOR_AI.txt")

    required_anchor = "https://ilyastas.github.io/katalog-ai/AUTHORITATIVE_COMPANY_LIST.json"

    if required_anchor not in readme:
        fail("README.md does not include AUTHORITATIVE_COMPANY_LIST.json in source list")

    if "Do not treat dataset names or section titles as companies" not in readme:
        fail("README.md is missing anti-confusion output rule")

    if "Authoritative-Company-Anchor:" not in ai_txt:
        fail("ai.txt is missing Authoritative-Company-Anchor entry")

    if "Dataset titles and category names are not company entities." not in start_here:
        fail("START_HERE_FOR_AI.txt is missing anti-confusion rule")

    print("OK: AI entrypoints contain canonical anchor and anti-confusion rules")


def main() -> None:
    check_canonical_counts()
    check_dataset_title_confusion()
    check_ai_entrypoints()
    print("PASS: AI integrity checks completed")


if __name__ == "__main__":
    main()
