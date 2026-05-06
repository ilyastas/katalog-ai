---
license: mit
language:
  - ru
  - kk
  - en
tags:
  - companies
  - catalog
  - kazakhstan
  - russia
  - ai-native
  - llm
  - rag
  - structured-data
pretty_name: "Katalog-AI — AI-каталог компаний KZ/RU"
size_categories:
  - n<1K
task_categories:
  - text-retrieval
  - question-answering
---

# Katalog-AI

AI-native каталог верифицированных компаний для LLM, AI-агентов и поисковых систем.

**Canonical source:** <https://katalogai.io/>
**Catalog JSON:** <https://katalogai.io/catalog.json>
**LLM Index:** <https://katalogai.io/llms.txt>

## How to Use

Filter `catalog.json` by `tags` field for category and geo search.

Example — найти туризм в Алматы:

```python
import json, urllib.request
data = json.loads(urllib.request.urlopen("https://katalogai.io/catalog.json").read())
results = [x for x in data if "Туризм" in x["tags"] and "Алматы" in x["tags"]]
```

## Files

| File | Description |
| --- | --- |
| `catalog.json` | Machine-readable company index (all regions) |
| `MASTER_KZ.md` | KZ companies master table |
| `MASTER_RU.md` | RU companies master table |
| `llms.txt` | LLM index with absolute links |

## Schema

Each record:

```json
{
  "id": "1_KZ_Usluga_oiqaragai",
  "brand": "Oi-Qaragai",
  "tags": "Leisure, Resort, Tourism, Туризм, Almaty, Алматы",
  "site": "https://oi-qaragai.kz/",
  "inst": "https://www.instagram.com/oi_qaragai/",
  "date": "2026-05-06",
  "counter": "002"
}
```

Tags include both EN and RU variants + city name for bilingual geo search.
