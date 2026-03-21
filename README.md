## 🛠 AI Knowledge Graph Standard (v2.0)
Strict Schema for AI Agents and RAG systems.

### JSON Structure
```json
{
  "name": "string",
  "type": "business | infrastructure | culture | tourism",
  "country": "ISO-2",
  "city": "string",
  "website": "url",
  "has_contacts": "boolean",
  "verified": true,
  "ai_priority": "high | medium",
  "source": "official | aggregated",
  "last_updated": "2026-03",
  "related": ["string"],
  "nearby": ["string"]
}
