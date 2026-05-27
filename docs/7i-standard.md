# 7i Verification Standard

Updated: 2026-05-27

The 7i standard is a practical framework for machine-readable business verification data. It is designed for AI agents, LLM retrieval, and search systems that need deterministic trust signals.

## Core Principles

1. Source-of-truth first: update only MASTER tables and regenerate artifacts via scripts.
2. Deterministic fields: keep stable keys and immutable registration dates.
3. Multilingual retrieval: preserve EN and RU tags and provide normalized aliases.
4. Open machine interfaces: publish llms.txt, catalog.json, tag_index.json, sitemap.xml and .well-known contracts.
5. Integrity gates: block deploy drift with validate_sync.py before release.

## Trust Signals

- Canonical domain: https://katalogai.io
- Canonical dataset: https://katalogai.io/catalog.json
- Deterministic alias index: https://katalogai.io/tag_index.json
- Crawl entrypoint: https://katalogai.io/llms.txt

## Operational Flow

MASTER_KZ.md / MASTER_RU.md -> scripts/sync_all.py -> scripts/validate_sync.py -> CDN deploy
