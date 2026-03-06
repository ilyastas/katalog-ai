const fs = require('fs');
const path = require('path');

function normalizeText(text) {
  return String(text || '').toLowerCase().trim();
}

function loadCompanies() {
  const filePath = path.join(__dirname, '..', 'data', 'companies.json');
  const raw = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(raw);
  return data.companies || [];
}

module.exports = (req, res) => {
  try {
    const category = normalizeText(req.query.category || req.params?.category || '');

    if (!category) {
      return res.status(400).json({ error: 'Category is required' });
    }

    const companies = loadCompanies();
    const results = companies
      .filter((c) => normalizeText(c.category) === category || normalizeText(c.category).includes(category))
      .sort((a, b) => (b.trust_score || 0) - (a.trust_score || 0));

    return res.status(200).json({ category, count: results.length, results });
  } catch (error) {
    return res.status(500).json({ error: 'Category lookup failed', detail: error.message });
  }
};
