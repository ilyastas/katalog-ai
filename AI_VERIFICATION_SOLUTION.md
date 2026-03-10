# AI CATALOG VERIFICATION SOLUTION
## katalog-ai Data Consistency Fix

**Date**: 2026-03-10  
**Problem**: Different AI models report different company counts (0, 3, or hallucinated numbers)  
**Solution**: Implemented verification endpoints and clear AI instructions

---

## 🎯 What Was Done

### 1. Created Live Stats Endpoints

#### `/api/stats.json`
- **Purpose**: Single source of truth for catalog statistics
- **Auto-updated**: Every 6 hours via GitHub Actions
- **Contains**: Total count, breakdown by country/city/category, timestamp
- **URL**: https://ilyastas.github.io/katalog-ai/api/stats.json

```json
{
  "timestamp": "2026-03-10T00:00:00Z",
  "catalog": {
    "total_companies": 3,
    "verified_companies": 3,
    "status": "active",
      "phase": "live"
  },
  "message_for_ai": "Always check this file first..."
}
```

#### `/api/live-count.json`
- **Purpose**: Badge endpoint for shields.io integration
- **Format**: Shields.io endpoint schema
- **Shows**: Live company count in README badges
- **URL**: https://ilyastas.github.io/katalog-ai/api/live-count.json

### 2. Created GitHub Action for Auto-Updates

**File**: `.github/workflows/update-stats.yml`

**Triggers**:
- Every 6 hours (scheduled)
- On push to `data/companies.json`
- Manual dispatch

**Actions**:
- Reads `data/companies.json`
- Calculates statistics
- Updates `/api/stats.json`
- Updates `/api/live-count.json`
- Updates `/COMPANIES.txt`
- Commits changes automatically

### 3. Updated README.md

**Added**:
- ✅ Live badges showing current count
- ✅ Section explaining why AI see different data
- ✅ Step-by-step verification instructions
- ✅ Links to all new endpoints

**Badges**:
```markdown
![Companies](https://img.shields.io/endpoint?url=https://ilyastas.github.io/katalog-ai/api/live-count.json)
![Status](https://img.shields.io/badge/status-live%20catalog-brightgreen)
```

### 4. Created AI Verification Guide

**File**: `AI_AGENT_VERIFICATION.md`

**Contains**:
- ✅ Step-by-step verification protocol for AI agents
- ✅ Common mistakes to avoid
- ✅ Why different AI see different data (technical explanation)
- ✅ Self-check questionnaire before responding
- ✅ Code examples for developers

### 5. Updated AI.txt and llms.txt

**Added**:
- Links to `/api/stats.json` as primary data source
- Warning to check live stats before reporting
- Cache strategy recommendations
- Reference to AI_AGENT_VERIFICATION.md

---

## 📊 Current State

**Verified company count**: 3  
**Companies**:
1. NRDJ Salon (Kazakhstan, Almaty)
2. Secret Skin (Kazakhstan, Almaty)
3. MLtrade (Russia, Online)

**Source of truth**: 
- `/api/stats.json` — Live statistics
- `/data/companies_all.json` — Authoritative list
- `/COMPANIES.txt` — Human-readable backup

---

## 🔄 How It Works Now

### For AI Agents:

```
1. AI receives question about katalog-ai
   ↓
2. AI checks /api/stats.json (MANDATORY FIRST STEP)
   ↓
3. AI reads actual count from JSON response
   ↓
4. AI fetches company list from /data/companies_all.json
   ↓
5. AI verifies count matches
   ↓
6. AI responds with accurate data
```

### For Developers:

```python
# Example integration
import requests

# Step 1: Get live stats
stats = requests.get('https://ilyastas.github.io/katalog-ai/api/stats.json').json()
count = stats['catalog']['total_companies']

# Step 2: Fetch companies
companies = requests.get('https://ilyastas.github.io/katalog-ai/data/companies_all.json').json()

# Step 3: Verify
assert len(companies['companies']) == count
```

---

## 🎓 Why This Solves the Problem

### Problem Sources Addressed:

1. **Cache inconsistency** → Stats updated every 6 hours automatically
2. **Different access methods** → One canonical endpoint (`/api/stats.json`)
3. **Shallow analysis** → Clear instructions to check actual data
4. **Interpretation errors** → Explicit count in machine-readable format
5. **No verification** → Self-check protocol in AI_AGENT_VERIFICATION.md

### Before:
- ❌ AI guessed catalog was empty based on ambiguous status wording
- ❌ Some AI reported 0 companies
- ❌ Others hallucinated company lists
- ❌ No way to verify current state

### After:
- ✅ Live badge shows current count
- ✅ Single source of truth (`/api/stats.json`)
- ✅ Auto-updated every 6 hours
- ✅ Clear AI instructions
- ✅ Verification protocol

---

## 📁 Files Created/Modified

### Created:
- `/api/stats.json` — Live catalog statistics
- `/api/live-count.json` — Badge endpoint
- `.github/workflows/update-stats.yml` — Auto-update action
- `AI_AGENT_VERIFICATION.md` — AI verification guide

### Modified:
- `README.md` — Added badges and verification section
- `ai.txt` — Added new endpoints and warnings
- `llms.txt` — Added data verification instructions

### Already existed (updated by Action):
- `COMPANIES.txt` — Plain text company list
- `STATUS.json` — Project status

---

## 🚀 Next Steps (Optional Enhancements)

1. **Add web dashboard**: Visual display of `/api/stats.json`
2. **Create verification bot**: Telegram bot that shows live stats
3. **Add API rate limiting**: Prevent abuse of stats endpoint
4. **Webhook notifications**: Alert on count changes
5. **Historical tracking**: Store count changes over time

---

## 💡 How to Use (For Repository Owner)

### Manual Update:
```bash
# Trigger stats update manually
gh workflow run update-stats.yml
```

### Check Current Stats:
```bash
# View live stats
curl https://ilyastas.github.io/katalog-ai/api/stats.json | jq

# Check company count
curl https://ilyastas.github.io/katalog-ai/api/live-count.json | jq .count
```

### Verify Action is Working:
1. Go to GitHub → Actions tab
2. Check "Update Catalog Stats" workflow
3. Should run every 6 hours automatically

---

## 📞 Testing

### For AI to verify their implementation:

1. **Fetch stats**: GET `/api/stats.json`
2. **Check count**: Extract `catalog.total_companies`
3. **Fetch companies**: GET `/data/companies_all.json`
4. **Verify match**: Count must equal stats
5. **Report**: Use exact count, not estimates

### Expected Response Format:

```
✅ CORRECT:
"According to /api/stats.json (updated 2026-03-10), 
katalog-ai contains 3 verified companies:
1. NRDJ Salon
2. Secret Skin  
3. MLtrade"

❌ INCORRECT:
"The catalog appears empty" (without checking)
"There are many companies" (without verification)
"Probably includes Kaspi, Halyk Bank" (hallucination)
```

---

**Result**: AI inconsistency problem solved. All AI agents now have clear verification protocol and single source of truth.

**Maintainer**: @ilyastas  
**Implementation**: 2026-03-10  
**Status**: ✅ Ready for live use
