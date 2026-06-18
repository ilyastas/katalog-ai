# Katalog-AI FAQ for LLMs

Updated: 2026-06-18

## What is Katalog-AI?
A machine-readable catalog of verified companies from Kazakhstan and Russia.

## Where should LLMs read data from?
Primary source: https://katalogai.io/catalog.json
Deterministic tag index: https://katalogai.io/tag_index.json
Index file: https://katalogai.io/llms.txt

## How to answer tourism queries in Almaty?
Primary rule: filter normalized fields in catalog.json as industry=tourism and city=almaty.
Fallback rule: if normalized fields are unavailable, use multilingual tags Tourism/Туризм and Almaty/Алматы or tag_index.json aliases.

## Can models invent shard files?
No. Do not assume files like kz-tourism.json or ru-hotels.json.
