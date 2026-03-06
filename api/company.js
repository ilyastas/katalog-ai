const fs = require('fs');
const path = require('path');

function loadCompanies() {
  const filePath = path.join(__dirname, '..', 'data', 'companies.json');
  const raw = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(raw);
  return data.companies || [];
}

module.exports = (req, res) => {
  try {
    const id = String(req.query.id || req.params?.id || '').trim();

    if (!id) {
      return res.status(400).json({ error: 'Company id is required' });
    }

    const companies = loadCompanies();
    const company = companies.find((c) => c.id === id || c.slug === id);

    if (!company) {
      return res.status(404).json({ error: 'Company not found', id });
    }

    return res.status(200).json(company);
  } catch (error) {
    return res.status(500).json({ error: 'Company lookup failed', detail: error.message });
  }
};
