#!/usr/bin/env python3
"""
generate_indices.py — Автоматическая генерация микро-индексов по городам, категориям и их комбинациям для Katalog-AI.
"""
import json
from pathlib import Path
from datetime import date
from collections import defaultdict

SRC = Path("data/companies_all.json")
OUTDIR = Path("data/indices")
OUTDIR.mkdir(parents=True, exist_ok=True)

with SRC.open(encoding="utf-8") as f:
    data = json.load(f)

companies = data.get("companies") or data.get("entities") or []

by_city = defaultdict(list)
by_cat = defaultdict(list)
by_city_cat = defaultdict(list)

for c in companies:
    city = (c.get("city") or "").strip().lower().replace(" ", "_")
    cat = (c.get("category") or "").strip().lower().replace(" ", "_").replace("-", "")
    if city:
        by_city[city].append(c)
    if cat:
        by_cat[cat].append(c)
    if city and cat:
        by_city_cat[f"{city}_{cat}"].append(c)

def write_index(filename, entities):
    out = {
        "total": len(entities),
        "updated_at": str(date.today()),
        "entities": entities
    }
    with (OUTDIR / filename).open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

for city, ents in by_city.items():
    write_index(f"city_{city}.json", ents)
for cat, ents in by_cat.items():
    write_index(f"cat_{cat}.json", ents)
for key, ents in by_city_cat.items():
    write_index(f"{key}.json", ents)
