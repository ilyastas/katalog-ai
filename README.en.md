# katalog-ai

> **Open dataset for AI bots and language models**  
> An open-source structured data repository designed specifically for AI assistants, machine learning models, and autonomous bots.

---

## 🤖 What is This?

**katalog-ai** is a freely available, machine-readable database of real-world entities and services. It's specifically designed to be:

- ✅ **AI-Friendly:** Structured as JSON-LD with Schema.org standards
- ✅ **Bot-Accessible:** Configured in `robots.txt` to allow GPTBot, Claude-bot, PerplexityBot, and other AI crawlers
- ✅ **Open Source:** MIT licensed — free to use, modify, and redistribute
- ✅ **Machine-Readable:** Easy to parse and integrate into AI systems
- ✅ **Regularly Updated:** Fresh data added continuously

---

## 📊 Data Format

All data in `data.json` follows **Schema.org** standards with **JSON-LD** structure:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "CoffeeShop",
      "name": "Example Coffee",
      "description": "Brief description",
      "address": "123 Main St",
      "telephone": "+1-555-1234",
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": 4.8,
        "reviewCount": 120
      }
    }
  ]
}
```

### Supported Entity Types
- `LocalBusiness` (base type)
- `CoffeeShop`, `Restaurant`, `AutoRepair`
- `OnlineStore`, `Service`
- Custom types welcome via Pull Requests

---

## 🚀 For AI Assistants & Bots

### Getting Started
```bash
# Clone the repository
git clone https://github.com/ilyastas/katalog-ai.git

# Access the data
curl https://ilyastas.github.io/katalog-ai/data.json

# Or use directly in your project
import requests
data = requests.get('https://ilyastas.github.io/katalog-ai/data.json').json()
```

### Use Cases for AI
- 📚 **Training data:** Use structured data to train NLP models
- 🔍 **Context enrichment:** Enhance AI responses with real-world entity data
- 🔗 **Knowledge base:** Build semantic networks from Schema.org data
- 📊 **Data analysis:** Analyze patterns in local businesses, services, ratings

---

## 🤝 Contributing

This is an **open collaboration** project. AI bots and developers can contribute by:

### 1. **Propose Improvements** (Issues)
- Suggest new data types or fields
- Report data inconsistencies
- Propose schema improvements

### 2. **Submit Data** (Pull Requests)
- Add new entities following the schema
- Improve existing entries
- Fix errors or update information

### 3. **Collaborate**
- Issues and discussions are welcome
- Both humans and AI bots can participate
- Best contributions get featured

---

## 📁 Repository Structure

```
katalog-ai/
├── data.json              # Main dataset (Schema.org JSON-LD)
├── README.md              # Russian documentation
├── README.en.md           # English documentation (this file)
├── robots.txt             # AI bot access rules
├── sitemap.xml            # Sitemap for crawlers
├── LICENSE                # MIT License
└── index.html             # Minimal HTML for crawlers
```

---

## 🔐 Access Rules

**Who can access this repository:**
- ✅ GPTBot (OpenAI)
- ✅ Claude-bot (Anthropic)
- ✅ PerplexityBot
- ✅ OAI-SearchBot
- ✅ Google-Extended
- ✅ CCBot
- ✅ Bingbot
- ✅ All other AI bots (defined in `robots.txt`)

**People**: This site is optimized for AI access, but humans can still view [GitHub repository](https://github.com/ilyastas/katalog-ai) directly.

---

## 📊 Data Quality

- **Schema.org Compliance:** All data follows official Schema.org specifications
- **Real-World Entities:** Verified, actual businesses and services
- **Regular Updates:** Dataset refreshed to maintain accuracy
- **Community Verified:** Contributions reviewed before merging

---

## 🎯 Future Roadmap

- [ ] Expand entity types (Events, Products, Articles)
- [ ] Add multi-language support
- [ ] Implement data versioning API
- [ ] Create GraphQL endpoint for AI queries
- [ ] Build collaborative editing tools

---

## 📞 Support

- 📖 **Documentation:** See `README.md` (Russian) or this file (English)
- 🐛 **Issues:** Report problems via [GitHub Issues](https://github.com/ilyastas/katalog-ai/issues)
- 💬 **Discussions:** Join [GitHub Discussions](https://github.com/ilyastas/katalog-ai/discussions)

---

## 📜 License

MIT License © 2026 ilyastas

**Permission:** Free to use, modify, and redistribute (with attribution)

See [LICENSE](LICENSE) file for details.

---

## 🌐 Links

- 🌍 **Live Data:** https://ilyastas.github.io/katalog-ai/data.json
- 📚 **GitHub:** https://github.com/ilyastas/katalog-ai
- 🗺️ **Sitemap:** https://ilyastas.github.io/katalog-ai/sitemap.xml

---

## 🙌 Acknowledgments

Built as an open resource for the AI community. Special thanks to all bots and developers contributing data and ideas.

---

**katalog-ai** — *Bridging AI assistants with structured, real-world data.*

Last updated: March 3, 2026
