#!/usr/bin/env python3
"""
Add Company Script
Interactive tool to add new company to catalog with validation.
Automatically updates all derived files.
"""

import json
import sys
import re
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
        print(f"✅ Saved: {filepath}")
    except Exception as e:
        print(f"❌ Error saving {filepath}: {e}")
        sys.exit(1)

def generate_slug(name):
    """Generate URL-friendly slug from company name."""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def get_next_id(companies_data):
    """Get next available company ID."""
    if not companies_data['companies']:
        return 'comp-0001'
    
    ids = [int(c['id'].split('-')[1]) for c in companies_data['companies']]
    next_num = max(ids) + 1
    return f"comp-{next_num:04d}"

def validate_url(url):
    """Basic URL validation."""
    url_pattern = re.compile(r'https?://[^\s]+')
    return bool(url_pattern.match(url))

def prompt_input(prompt, required=True, validator=None):
    """Get validated user input."""
    while True:
        value = input(prompt).strip()
        
        if not value and required:
            print("⚠️  This field is required. Please try again.")
            continue
        
        if validator and not validator(value):
            print("⚠️  Invalid input. Please try again.")
            continue
        
        return value

def main():
    """Interactive company addition."""
    print("=" * 60)
    print("📝 ADD NEW COMPANY TO CATALOG")
    print("=" * 60)
    
    # Load existing data
    companies_path = Path('data/companies.json')
    companies_data = load_json(companies_path)
    
    print(f"\n📊 Current catalog: {companies_data['count']} companies")
    print("\nEnter company details (Ctrl+C to cancel):\n")
    
    try:
        # Collect company data
        name = prompt_input("Company name: ")
        slug = generate_slug(name)
        print(f"   Generated slug: {slug}")
        
        category = prompt_input("Category (e.g., Beauty and Personal Care): ")
        service = prompt_input("Service (e.g., Hair Salon, E-commerce): ")
        
        country = prompt_input("Country (e.g., Kazakhstan, Russia): ")
        city = prompt_input("City (e.g., Almaty, Moscow): ")
        
        url = prompt_input("Main URL: ", validator=validate_url)
        
        # Verification sources
        print("\nVerification sources (comma-separated, e.g., instagram, website):")
        sources_str = prompt_input("Sources: ")
        sources = [s.strip() for s in sources_str.split(',')]
        
        # Optional fields
        print("\n--- Optional Fields (press Enter to skip) ---")
        phone = prompt_input("Phone: ", required=False)
        email = prompt_input("Email: ", required=False)
        
        instagram = prompt_input("Instagram URL: ", required=False)
        telegram = prompt_input("Telegram URL: ", required=False)
        whatsapp = prompt_input("WhatsApp URL: ", required=False)
        
        description = prompt_input("Description: ", required=False)
        
        # Keywords
        keywords_str = prompt_input("Semantic keywords (comma-separated): ", required=False)
        keywords = [k.strip() for k in keywords_str.split(',')] if keywords_str else []
        
        # Build company object
        company_id = get_next_id(companies_data)
        company = {
            'id': company_id,
            'name': name,
            'slug': slug,
            'category': category,
            'service': service,
            'country': country,
            'city': city,
            'url': url,
            'contact': {},
            'social': {},
            'verification': {
                'status': 'verified',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sources': sources
            },
            'metrics': {
                'rating': 0.0,
                'reviews_count': 0,
                'followers': 0
            },
            'semantic_keywords': keywords,
            'added_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Add optional contact fields
        if phone:
            company['contact']['phone'] = phone
        if email:
            company['contact']['email'] = email
        
        # Add optional social fields
        if instagram:
            company['social']['instagram'] = instagram
        if telegram:
            company['social']['telegram'] = telegram
        if whatsapp:
            company['social']['whatsapp'] = whatsapp
        
        if description:
            company['description'] = description
        
        # Preview
        print("\n" + "=" * 60)
        print("📋 COMPANY PREVIEW")
        print("=" * 60)
        print(json.dumps(company, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        # Confirm
        confirm = input("\n✅ Add this company to catalog? (yes/no): ").lower()
        if confirm not in ['yes', 'y']:
            print("❌ Operation cancelled.")
            return
        
        # Add to companies array
        companies_data['companies'].append(company)
        companies_data['count'] = len(companies_data['companies'])
        companies_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # Save master file
        save_json(companies_path, companies_data)
        
        print(f"\n✅ Company '{name}' added successfully!")
        print(f"   ID: {company_id}")
        print(f"   Total companies: {companies_data['count']}")
        
        print("\n📋 Next steps:")
        print("   1. Run: python scripts/sync_catalogs.py")
        print("   2. Review generated files")
        print("   3. Commit changes to git")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
