# Catalog Status Policy

This policy defines canonical terminology for catalog lifecycle status across docs, JSON payloads, and automation.

## Canonical Terms

- `live`: The catalog is active and publicly usable with real business data.
- `active`: Operational state for endpoints/services.
- `empty`: No records currently present.

## Terms To Avoid In Catalog Status Context

- `pilot`
- `mvp`
- `production` (for catalog lifecycle label)
- `data pending`

Note: `production` is still valid for deployment environments (for example CI/CD pipeline environment names), but not for catalog lifecycle labels.

## Required Field Values

- `STATUS.json`:
  - `status`: `LIVE`
- `api/stats.json`:
  - `catalog.status`: `active` or `empty`
  - `catalog.phase`: `live` or `empty`
- `api/live-count.json`:
  - `status`: `active` or `empty`
  - `phase`: `live` or `empty`
- `data/companies.json` metadata:
  - Use wording `Active live catalog` when records exist.

## Automation Rule

Workflow `.github/workflows/update-stats.yml` must generate:

- `phase = "live"` when `total > 0`
- `phase = "empty"` when `total == 0`

## Enforcement Checklist

Before merge, run checks:

1. Search for forbidden catalog-status terms in root docs and API payload files.
2. Validate JSON phase/status values are in allowed set.
3. Confirm workflow generator still outputs `live/empty` only.
