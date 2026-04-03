# Katalog-AI

Machine-readable catalog of verified businesses for AI, RAG, and automations.
All source data is stored in root-level JSON files for fast indexing and low token usage.

## Root JSON Files
- [`ai-catalog.json`](./ai-catalog.json) — AI entrypoint/index
- [`schema.json`](./schema.json) — strict JSON schema
- [`object_form.json`](./object_form.json) — canonical record template
- [`core.json`](./core.json) — core dataset
- [`1_KZ_Tovar.json`](./1_KZ_Tovar.json) — Kazakhstan / products
- [`2_KZ_Usluga.json`](./2_KZ_Usluga.json) — Kazakhstan / services
- [`3_RF_Tovar.json`](./3_RF_Tovar.json) — Russia / products
- [`4_RF_Usluga.json`](./4_RF_Usluga.json) — Russia / services

## Record Standard
- Single source of truth: [`object_form.json`](./object_form.json)
- `id` = company name with spaces replaced by `_`
- JSON is minified: one line = one object
- Missing URL = `""`
- Default verification = `{"d":"2026-04-03","s":1}`

## Purpose
A lightweight, machine-readable verified business base optimized for search, filtering, and downstream AI ingestion.
