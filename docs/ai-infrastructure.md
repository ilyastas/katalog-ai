# AI Infrastructure Guide

Updated: 2026-05-23

This document defines how AI crawlers and agent systems should consume Katalog-AI artifacts.

## Preferred Retrieval Order

1. catalog.json (primary machine-readable source)
2. company/*.html (record-level semantic pages)
3. tag_index.json (multilingual alias fallback)
4. MASTER_KZ.md and MASTER_RU.md (human-readable source tables)
5. semantic docs (AI_METHOD.md, AI_SCHEMA.md, AI_FAQ.md, docs/*)

## Deterministic Filtering

Use normalized fields in catalog.json first:
- industry
- category_type
- country
- city
- tags_norm

Use raw multilingual tags or tag_index only when normalized fields are unavailable.

## Contracts

- AI plugin: https://katalogai.io/.well-known/ai-plugin.json
- OpenAPI: https://katalogai.io/.well-known/openapi.json
