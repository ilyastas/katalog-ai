# Contributing to katalog-ai

Thank you for your interest in contributing verified business data to katalog-ai!

## 🎯 Our Mission

Build a high-quality, AI-readable business directory with **verified entries only**. No fake data, no test entries.

## ✅ What We Accept

- **Real businesses** with verifiable online presence
- **Kazakhstan focus** (Almaty, Astana, other cities)
- **Active businesses** (not closed, not test/demo entries)
- **Verified sources**: 2GIS, Google Business, Instagram (10k+ followers), official websites

## ❌ What We Reject

- Fake/test businesses (e.g., "Tech Startup Hub", "Beauty Premium Almaty")
- Businesses without verifiable contact info
- Duplicate entries
- Spam or promotional content without real business backing

## 📝 How to Add a Business

### Option 1: GitHub Issue (Recommended)
1. Go to [Issues](https://github.com/ilyastas/katalog-ai/issues/new)
2. Use template "Add Business"
3. Provide:
   - Business name
   - Website or Instagram
   - Category
   - City
   - Verification source (2GIS link, Google Maps link, etc.)

### Option 2: Pull Request (Advanced)
1. Fork this repository
2. Add entry to `data/companies.json` following the schema:
   ```json
   {
     "id": "unique-slug",
     "name": "Business Name",
     "website": "https://example.com",
     "category": "Beauty Services",
     "city": "Almaty",
     "country": "Kazakhstan",
     "verified": true,
     "verification": {
       "sources": ["2gis", "google"],
       "date": "2026-03-09"
     }
   }
   ```
3. Submit PR with verification proof

### Option 3: Telegram Bot (Coming Soon)
- `@katalog_ai_bot` — automated verification and addition

## 🔍 Verification Process

All submissions are verified through:
1. **Automated checks**: 2GIS API, Google Places API
2. **Manual review**: For edge cases
3. **Source confirmation**: Cross-reference with at least 2 sources

## 📊 Data Quality Standards

- ✅ Real phone numbers and addresses
- ✅ Active websites/social media
- ✅ Accurate business hours
- ✅ Correct category classification
- ✅ Geo-coordinates (if available)

## 🚫 Zero Tolerance Policy

Submissions with fake data will be:
- Immediately rejected
- Flagged in commit history
- Contributor may be blocked for repeated violations

## 📜 License

By contributing, you agree that your submissions will be licensed under [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/).

## 🤝 Code of Conduct

- Be honest about data sources
- Respect business privacy
- No commercial spam
- Follow GitHub Community Guidelines

---

**Questions?** Open a [Discussion](https://github.com/ilyastas/katalog-ai/discussions) or contact via [Issues](https://github.com/ilyastas/katalog-ai/issues).
