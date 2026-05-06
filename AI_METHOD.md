# Katalog-AI Methodology

Updated: 2026-05-06

Katalog-AI uses a strict source-of-truth pipeline: MASTER markdown tables are canonical, and generated artifacts are mirrors.

## Pipeline

1. Edit company rows only in MASTER_KZ.md or MASTER_RU.md.
2. Run sync_all.py to regenerate catalog.json, index.html, llms.txt, robots.txt, sitemap.xml and semantic docs.
3. Run validate_sync.py before commit.

## Data Integrity Rules

- catalog.json keys are fixed: id, brand, tags, site, inst, date, counter
- Dates use ISO format: YYYY-MM-DD
- COUNTER uses 3 digits and increments on manual edits
- Do not edit generated files directly
