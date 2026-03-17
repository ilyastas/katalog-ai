#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from datetime import date
from collections import defaultdict

SRC = Path("data/companies_all.json")
OUTDIR = Path("data/indices")
SUMMARY_FILE = OUTDIR / "summary.json"

# 1. Очистка старых индексов (чтобы не плодить мусор)
if OUTDIR.exists():
    shutil.rmtree(OUTDIR)
OUTDIR.mkdir(parents=True, exist_ok=True)


with SRC.open(encoding="utf-8") as f:
    raw_data = json.load(f)

# Логика "Всеядности": поддержка [] и {"companies": []}
if isinstance(raw_data, list):
    companies = raw_data
elif isinstance(raw_data, dict):
    companies = raw_data.get("companies") or raw_data.get("entities") or []
else:
    companies = []

by_city = defaultdict(list)
by_cat = defaultdict(list)
by_city_cat = defaultdict(list)
indices_map = [] # Для summary.json

# 2. Обработка данных
for c in companies:
    # Нормализация (убираем лишние пробелы и странные символы)
    city = (c.get("city") or "").strip().lower().replace(" ", "_")
    cat = (c.get("category") or "").strip().lower().replace(" ", "_").replace("-", "")
    
    if city: by_city[city].append(c)
    if cat: by_cat[cat].append(c)
    if city and cat: by_city_cat[f"{city}_{cat}"].append(c)

def write_index(filename, entities, description):
    out = {
        "index_info": {
            "description": description,
            "updated_at": str(date.today()),
            "source": "https://github.com/ilyastas/katalog-ai"
        },
        "total": len(entities),
        "entities": entities
    }
    with (OUTDIR / filename).open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    indices_map.append(filename)

# 3. Генерация файлов срезов
for city, ents in by_city.items():
    write_index(f"city_{city}.json", ents, f"Verified businesses in {city.capitalize()}")

for cat, ents in by_cat.items():
    write_index(f"cat_{cat}.json", ents, f"Business category: {cat.replace('_', ' ').capitalize()}")

for key, ents in by_city_cat.items():
    write_index(f"{key}.json", ents, f"Filtered index for {key.replace('_', ' ')}")

# 4. Генерация Умного Summary для ИИ
summary = {
    "api_version": "1.0-ai",
    "last_updated": str(date.today()),
    "available_cities": sorted(list(by_city.keys())),
    "available_categories": sorted(list(by_cat.keys())),
    "index_files": sorted(indices_map)
}

with SUMMARY_FILE.open("w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"✅ Успешно! Создано {len(indices_map)} индексов и файл summary.json")
