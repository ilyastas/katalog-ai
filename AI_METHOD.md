# Katalog-AI Methodology

Updated: 2026-05-08

Katalog-AI uses a strict source-of-truth pipeline: MASTER markdown tables are canonical, and generated artifacts are mirrors.

## Pipeline

1. Edit company rows only in MASTER_KZ.md or MASTER_RU.md.
2. Run scripts/sync_all.py to regenerate catalog.json, index.html, llms.txt, robots.txt, sitemap.xml and semantic docs.
3. Run scripts/validate_sync.py before commit.

## Add New Company (Instruction)

1. Insert a new row into MASTER_KZ.md or MASTER_RU.md only.
2. Fill all required columns: ID, brand, tags, site, inst, date, counter (and wikidata when column exists).
3. Keep ID stable and region-marked (KZ or RU).
4. Keep tags bilingual (EN + RU) and include geo tags where relevant.
5. Run sync_all.py and then validate_sync.py.
6. Never edit generated outputs directly.

## Daily Date/Counter Update (Instruction)

- sync_all.py performs daily bump for both date and counter in all MASTER rows.
- counter is always 3-digit and incremented by +1 per daily run.
- validate_sync.py enforces that MASTER dates match today and generated artifacts stay in sync.

## Data Integrity Rules

- catalog.json keys: id, brand, tags, site, inst, date, counter; optional: wikidata (Wikidata QID, e.g. Q139710659)
- Dates use ISO format: YYYY-MM-DD
- COUNTER uses 3 digits and increments on every daily sync
- Do not edit generated files directly
