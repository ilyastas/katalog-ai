# LLM Query Templates for katalog-ai

Use these templates to force models to read the authoritative dataset and avoid hallucinations.

## Authoritative Endpoints
- Company list (plain): `https://ilyastas.github.io/katalog-ai/data/companies_all.json`
- Full records: `https://ilyastas.github.io/katalog-ai/data/companies.json`
- Catalog map: `https://ilyastas.github.io/katalog-ai/data/index.json`

## Rules to Include in Any Prompt
- Use only the provided URL(s).
- Do not use prior memory or external sources.
- Output count must equal `count` in JSON.
- If endpoint is unavailable, report that explicitly.

## 1) Gemini Template
```text
Use ONLY this endpoint:
https://ilyastas.github.io/katalog-ai/data/companies_all.json

Task:
Return the FULL company list from companies[].

Output format:
1. <name> - <url>
2. <name> - <url>
...

Validation:
- Number of output rows must equal JSON field count.
- Do not add any companies from memory.
- If endpoint is unavailable, return: SOURCE_UNAVAILABLE.
```

## 2) ChatGPT Template
```text
Read ONLY:
https://ilyastas.github.io/katalog-ai/data/companies_all.json

Goal:
Extract all companies from companies[] and print a numbered list.

Required format:
1. <name> | <category> | <country>/<city> | <url>

Hard constraints:
- Use no external knowledge.
- Ensure list length equals count.
- If mismatch detected, print: COUNT_MISMATCH and stop.
```

## 3) Claude Template
```text
Data source (strict):
https://ilyastas.github.io/katalog-ai/data/companies_all.json

Please:
- Parse JSON.
- Output all entries from companies[] in a table:
  name | slug | category | verification_status | url
- Add final line: total=<n>, expected=<count>, ok=<true/false>

Rules:
- No assumptions.
- No additional entities.
```

## 4) DeepSeek Template
```text
Use strictly this JSON endpoint:
https://ilyastas.github.io/katalog-ai/data/companies_all.json

Return:
- Complete list of company names.
- Then detailed list:
  - name
  - slug
  - category
  - country
  - city
  - url

Verification step:
Compare extracted item count with JSON count and print PASS/FAIL.
```

## 5) Perplexity Template
```text
Cite only this source URL:
https://ilyastas.github.io/katalog-ai/data/companies_all.json

Task:
Provide the exact company list from companies[] with no external additions.

Output:
- Bullet list of names
- Then: "Source count=<count>, extracted=<n>"

Constraint:
If any company is not present in the JSON, do not include it.
```

## Optional: Full Record Prompt
```text
Use ONLY:
https://ilyastas.github.io/katalog-ai/data/companies.json

Return full objects for each company with fields:
name, slug, category, verification.status, verification.sources, url.
Validate extracted object count equals count.
```

## Quick Sanity Check Command
```bash
curl -s https://ilyastas.github.io/katalog-ai/data/companies_all.json
```
