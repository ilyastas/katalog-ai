# LLM Guardrails

Purpose: prevent hallucinated company lists and force factual answers from repository JSON.

## Scope

This repository is a structured JSON directory. Models must behave as deterministic data parsers, not market analysts.

## Canonical Data Sources

Read in this order:
1. `https://ilyastas.github.io/katalog-ai/api/stats.json`
2. `https://ilyastas.github.io/katalog-ai/data/companies_all.json`
3. `https://ilyastas.github.io/katalog-ai/data/companies.json`

If local files are used, read:
1. `/api/stats.json`
2. `/data/companies_all.json`
3. `/data/companies.json`

## Hard Rules

1. Use only JSON data from canonical sources above.
2. Do not inject external market knowledge or famous company names.
3. Report `count` exactly as provided by source JSON.
4. List company names exactly as provided by source JSON.
5. If source cannot be read, return exactly `SOURCE_UNAVAILABLE`.
6. Never invent categories, metrics, or audit criteria not present in JSON.

## Output Contract

Return results in this format:

```text
count: <number>
companies:
- <name_1>
- <name_2>
- <name_3>
source:
- <url_or_path_1>
- <url_or_path_2>
- <url_or_path_3>
```

If unavailable:

```text
SOURCE_UNAVAILABLE
```

## Strict Prompt Contracts

### Gemini

```text
Проведи аудит данных в репозитории https://github.com/ilyastas/katalog-ai.

СТРОГОЕ ОГРАНИЧЕНИЕ:
- Не используй общие знания о рынке ИИ или крупных компаниях.
- Работай только как парсер JSON-источников репозитория.

Сделай шаги:
1) Прочитай api/stats.json.
2) Прочитай data/companies_all.json.
3) Прочитай data/companies.json.
4) Возьми count только из JSON.
5) Выведи список компаний только из JSON.

Формат ответа:
count: <number>
companies:
- <name>
- <name>
- <name>
source:
- <path_or_url>
- <path_or_url>
- <path_or_url>

Если любой источник недоступен, ответь ровно: SOURCE_UNAVAILABLE
```

### Claude

```text
You are a strict JSON auditor. Do not use prior world knowledge.
Only read these sources in order:
1) /api/stats.json
2) /data/companies_all.json
3) /data/companies.json

Rules:
- Output count exactly from JSON.
- Output company names exactly from JSON.
- Do not add any company not present in JSON.
- If sources are unavailable, output exactly: SOURCE_UNAVAILABLE

Required output:
count: <number>
companies:
- <name>
source:
- <path_or_url>
```

### ChatGPT

```text
Выполни роль строгого аудитора JSON-данных репозитория.

Читай только:
1. /api/stats.json
2. /data/companies_all.json
3. /data/companies.json

Запрещено:
- использовать внешние знания о рынке ИИ;
- подставлять известные компании;
- придумывать категории и критерии, если их нет в JSON.

Обязательно:
- вернуть count точно из источника;
- перечислить только компании из JSON;
- приложить список использованных источников.

Если не удалось прочитать JSON, ответ должен быть ровно:
SOURCE_UNAVAILABLE
```

## Quick Verification Checklist

1. `count` in output equals `count` in `companies_all.json`.
2. Every listed company exists in `companies_all.json`.
3. No extra companies appear in output.
4. Sources are explicitly listed.
5. Fallback `SOURCE_UNAVAILABLE` is used when needed.
