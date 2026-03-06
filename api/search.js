const fs = require('fs');
const path = require('path');

function normalizeText(text) {
  return String(text || '')
    .toLowerCase()
    .replace(/[^a-z0-9а-яё\s-]/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function loadCompanies() {
  const filePath = path.join(__dirname, '..', 'data', 'companies.json');
  const raw = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(raw);
  return data.companies || [];
}

module.exports = (req, res) => {
  try {
    const q = normalizeText(req.query.q || '');
    const category = normalizeText(req.query.category || '');
    const city = normalizeText(req.query.city || '');
    const limit = Math.max(1, Math.min(Number(req.query.limit) || 10, 50));

    const companies = loadCompanies();

    const results = companies
      .filter((c) => {
        const haystack = normalizeText([
          c.name,
          c.service,
          c.category,
          c.city,
          c.description,
          (c.services || []).join(' '),
          (c.languages || []).join(' ')
        ].join(' '));

        const queryOk = !q || haystack.includes(q);
        const categoryOk = !category || normalizeText(c.category).includes(category);
        const cityOk = !city || normalizeText(c.city).includes(city);

        return queryOk && categoryOk && cityOk;
      })
      .sort((a, b) => (b.trust_score || 0) - (a.trust_score || 0))
      .slice(0, limit);

    res.status(200).json({
      query: req.query.q || '',
      category: req.query.category || null,
      city: req.query.city || null,
      count: results.length,
      results
    });
  } catch (error) {
    res.status(500).json({ error: 'Search failed', detail: error.message });
  }
};
