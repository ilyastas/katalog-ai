#!/usr/bin/env python3
"""
Sync Catalogs Script
Automatically generates derived files from master data/companies.json:
- data/companies_all.json (minimal list)
- COMPANIES.txt (plain text)
- Updates README.md company list section
- Validates count consistency
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        sys.exit(1)

def save_json(filepath, data):
    """Save JSON file with proper formatting."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated: {filepath}")
    except Exception as e:
        print(f"❌ Error saving {filepath}: {e}")
        sys.exit(1)

def generate_companies_all(companies_data):
    """Generate minimal companies_all.json from full companies.json."""
    companies_minimal = []
    
    for company in companies_data['companies']:
        companies_minimal.append({
            'id': company['id'],
            'name': company['name'],
            'slug': company['slug'],
            'category': company['category'],
            'country': company['country'],
            'city': company['city'],
            'url': company['url'],
            'verification_status': company['verification']['status']
        })
    
    return {
        'version': '1.0.0',
        'timestamp': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'authoritative': True,
        'source': 'https://ilyastas.github.io/katalog-ai/data/companies.json',
        'count': companies_data['count'],
        'companies': companies_minimal
    }

def generate_companies_txt(companies_data):
    """Generate plain text COMPANIES.txt."""
    lines = [
        'COMPANY LIST - katalog-ai',
        f"Last updated: {datetime.now().strftime('%Y-%m-%d')}",
        f"Total: {companies_data['count']} verified companies",
        ''
    ]
    
    for idx, company in enumerate(companies_data['companies'], 1):
        lines.append(f"{idx}. {company['name']}")
        lines.append(f"   Category: {company['category']}")
        lines.append(f"   Location: {company['country']}, {company['city']}")
        lines.append(f"   URL: {company['url']}")
        
        sources = ', '.join(company['verification']['sources'])
        lines.append(f"   Verified: {sources}")
        lines.append('')
    
    lines.append('---')
    lines.append('Source: https://ilyastas.github.io/katalog-ai/data/companies_all.json')
    
    return '\n'.join(lines)

def generate_readme_section(companies_data):
    """Generate README.md company list section."""
    lines = [
        '### 📋 Current Company List (count: {})'.format(companies_data['count']),
        ''
    ]
    
    for idx, company in enumerate(companies_data['companies'], 1):
        # Get Instagram or generic URL icon
        icon = '🔗'
        if 'instagram.com' in company['url']:
            icon = '📸'
        elif 'wildberries' in company['url']:
            icon = '🛒'
        
        lines.append(f"{idx}. **{company['name']}** — {company.get('service', company['category'])} ({company['country']}, {company['city']})")
        lines.append(f"   {icon} {company['url']}")
        
        sources = ', '.join(company['verification']['sources'])
        lines.append(f"   ✅ Verified: {sources}")
        lines.append('')
    
    date_str = datetime.now().strftime('%B %d, %Y')
    lines.append(f"> **Last updated:** {date_str} | **Sources:** [companies_all.json](https://ilyastas.github.io/katalog-ai/data/companies_all.json) | [COMPANIES.txt](./COMPANIES.txt)")
    
    return '\n'.join(lines)

def main():
    """Main sync routine."""
    print("🔄 Starting catalog synchronization...")
    
    # Load master data
    companies_path = Path('data/companies.json')
    if not companies_path.exists():
        print(f"❌ Master file not found: {companies_path}")
        sys.exit(1)
    
    companies_data = load_json(companies_path)
    count = companies_data['count']
    actual_count = len(companies_data['companies'])
    
    # Validate count
    if count != actual_count:
        print(f"⚠️  WARNING: count={count} but actual entries={actual_count}")
        print("   Fixing count in master file...")
        companies_data['count'] = actual_count
        save_json(companies_path, companies_data)
    
    print(f"📊 Processing {actual_count} companies...")
    
    # Generate companies_all.json
    companies_all = generate_companies_all(companies_data)
    save_json(Path('data/companies_all.json'), companies_all)
    
    # Generate COMPANIES.txt
    companies_txt = generate_companies_txt(companies_data)
    with open('COMPANIES.txt', 'w', encoding='utf-8') as f:
        f.write(companies_txt)
    print("✅ Updated: COMPANIES.txt")
    
    # Generate README section
    readme_section = generate_readme_section(companies_data)
    print("\n📝 README.md section (copy manually if needed):")
    print("=" * 60)
    print(readme_section)
    print("=" * 60)
    
    print(f"\n✅ Synchronization complete! Total companies: {actual_count}")
    print("\n📋 Next steps:")
    print("   1. Review generated files")
    print("   2. Update README.md with new company list section (see above)")
    print("   3. Run: git add data/companies_all.json COMPANIES.txt README.md")
    print("   4. Run: git commit -m 'Sync catalog files'")

if __name__ == '__main__':
    main()
