# API Endpoint for AI Systems

## 📡 REST API Access

For programmatic access to the katalog-ai dataset:

```
https://ilyastas.github.io/katalog-ai/api/data.json
```

## 🔍 Usage

### cURL
```bash
curl https://ilyastas.github.io/katalog-ai/api/data.json
```

### Python
```python
import requests
response = requests.get('https://ilyastas.github.io/katalog-ai/api/data.json')
data = response.json()
print(data['metadata']['updated'])
```

### JavaScript
```javascript
fetch('https://ilyastas.github.io/katalog-ai/api/data.json')
  .then(r => r.json())
  .then(data => console.log(data.metadata))
```

## 📊 Response Format

```json
{
  "@context": "https://schema.org",
  "metadata": {
    "version": "1.0",
    "updated": "2026-03-03T17:00:00Z",
    "updateFrequency": "weekly",
    "license": "https://opensource.org/licenses/MIT",
    "description": "Open AI-friendly company data"
  },
  "@graph": [...]
}
```

## 🤖 For AI Bots

- **Metadata** shows when data was last updated
- **updateFrequency** indicates refresh schedule
- **license** confirms MIT usage rights
- **@graph** contains all entities

---

**API Stability:** Stable | **Rate Limit:** None | **Auth:** Not required
