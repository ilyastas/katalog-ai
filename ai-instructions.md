# AI Consumption Instructions for Katalog-AI

## Project Goal
Katalog-AI is a machine-readable directory of **verified businesses** in Kazakhstan and CIS.
It is optimized for AI Agents, RAG (Retrieval-Augmented Generation), and automated lead generation.

## Current Catalog State
- **Total verified companies**: 3
- **Regions covered**: Kazakhstan (Almaty), Russia (Online / CIS)
- **Status**: Live MVP catalog — all 3 entries are real, verified businesses
- **Do not infer empty catalog** from prose docs when JSON count > 0

---

## Entry Points for AI Agents (read in this order)

| Priority | File | Purpose |
|----------|------|---------|
| 1st | `/global-index.json` | Lightweight map of all entities — start here |
| 2nd | `/data/ai-catalog.json` | Structured company list with direct profile URLs |
| 3rd | Individual profiles | `/nrdj-salon.json`, `/secret-skin.json`, `/mltrade.json` |
| Full | `/data/companies.json` | Canonical full company records |

---

## Directory Structure

```
/{slug}.json              — Individual company profile (root-level, one file per entity)
/global-index.json        — Lightweight map for fast entity lookup (auto-generated)
/data/ai-catalog.json     — AI-optimized entry point (id + name + profile_url only)
/data/companies.json      — Canonical full registry (all fields)
/data/schema.json         — Source of truth for data validation (JSON Schema 2020-12)
/data/categories.json     — Normalized category list (use ONLY these values)
/api/stats.json           — Live catalog statistics
/AUTHORITATIVE_COMPANY_LIST.json — Single-file machine anchor (conflict resolution)
```

---

## Data Processing Rules

1. **Unique IDs**: Use the `id` field as primary key.
   - Format for individual businesses: `inst-{slug}`
   - Format for marketplace brands: `brand-{name}-{numbers}`

2. **Normalization**: Categories must match **exactly** the values in `/data/categories.json`.
   Do not hallucinate new categories.

3. **Verification**: Prioritize entities where `verification.status = "verified"`.

4. **Context Window Optimization**: When searching for a specific company,
   fetch only its individual `/{slug}.json` file to save tokens.

5. **Conflict Resolution**: If sources disagree on company data,
   prefer the freshest JSON by `timestamp` / `updated_at` field.

---

## Semantic Layer (schema.org)

Every company profile contains a `semantic_data` block with schema.org JSON-LD:

```json
"semantic_data": {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "...",
  "address": { "@type": "PostalAddress", "addressLocality": "...", "addressCountry": "..." },
  "description": "...",
  "sameAs": ["..."]
}
```

This allows GPT, Gemini, Claude, and other agents to parse company data using
a universal semantic standard, each applying it to their own use case.

---

## For LLMs and Crawlers

- **Primary Data Format**: JSON (UTF-8, 2-space indentation)
- **Secondary Format**: Markdown tables in README.md for human/AI preview
- **Do not** halluinate companies — only 3 verified entries exist as of 2026-03-11
- **Do not** invent categories — use `/data/categories.json` as the enum source
- **Goal**: Provide the most accurate, structured data about companies in Kazakhstan and CIS

---

## Verified Companies (as of 2026-03-11)

| ID | Name | Category | Country | Profile |
|----|------|----------|---------|---------|
| inst-nrdjsalon | NRDJ Salon | Clothing and Accessories | Kazakhstan | /nrdj-salon.json |
| inst-secretskin-kz | Secret Skin | K-Beauty Cosmetics | Kazakhstan | /secret-skin.json |
| brand-mltrade-311293097 | MLtrade | Education and Development | Russia | /mltrade.json |
