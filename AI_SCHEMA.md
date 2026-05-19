# Katalog-AI Data Schema

Updated: 2026-05-19

Each catalog entry is an object with these fields:

- id: stable record id, includes region marker (KZ or RU)
- brand: company name
- tags: comma-separated semantic tags
- site: primary website URL
- inst: Instagram URL or '-'
- date: registration date in the catalog (set once on entry, immutable)
- wikidata: Wikidata QID or '-' if not available
- industry: canonical industry label
- category_type: canonical business type
- country: canonical country
- city: canonical city or '-'
- tags_norm: normalized lowercase tags (EN canonical vocabulary)

Machine endpoint: https://katalogai.io/catalog.json
