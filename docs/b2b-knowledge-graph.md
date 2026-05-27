# B2B Knowledge Graph Notes

Updated: 2026-05-27

Katalog-AI models business entities as a lightweight graph that combines deterministic IDs, regional context, semantic tags, and external references.

## Entity Layers

- Organization node: id, brand, site, inst, optional wikidata
- Semantic node: tags, tags_norm, industry, category_type
- Geo node: country, city, region inferred from id
- Navigation node: company page URL and canonical dataset URL

## Why It Matters for LLMs

- Stable IDs reduce hallucinated joins across sources.
- Normalized tags improve multilingual retrieval precision.
- Company pages provide human-readable anchors for citations.

## Scope

Current scope is Kazakhstan and Russia entries in one unified machine-readable catalog.
