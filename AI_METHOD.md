# Katalog-AI Methodology

Updated: 2026-05-19

Katalog-AI uses a strict source-of-truth pipeline: MASTER markdown tables are canonical, and generated artifacts are mirrors.

## Pipeline

1. Edit company rows only in MASTER_KZ.md or MASTER_RU.md.
2. Run scripts/sync_all.py to regenerate catalog.json, index.html, llms.txt, robots.txt, sitemap.xml and semantic docs.
3. Run scripts/validate_sync.py before commit.

## Add New Company (Instruction)

1. Insert a new row into MASTER_KZ.md or MASTER_RU.md only.
2. Fill all required columns: ID, brand, tags, site, inst, date (registration date, immutable) and wikidata (optional, use '-' if absent).
3. Keep ID stable and region-marked (KZ or RU).
4. Keep tags bilingual (EN + RU) and include geo tags where relevant.
5. Run sync_all.py and then validate_sync.py.
6. Never edit generated outputs directly.

## Date Policy

- sync_all.py does NOT perform daily mass bump for MASTER rows.
- date for a company is updated only when that company record changes.
- generated metadata dates follow build date (today).

## Data Integrity Rules

- catalog.json core keys: id, brand, tags, site, inst, date; optional: wikidata (Wikidata QID, e.g. Q139710659)
- catalog.json normalized keys: industry, category_type, country, city, tags_norm
- Dates use ISO format: YYYY-MM-DD
- date is the registration date in the catalog (immutable after first entry)
- Do not edit generated files directly
