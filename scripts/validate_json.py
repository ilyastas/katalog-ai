#!/usr/bin/env python3
"""
Validate JSON Script
Validates all catalog JSON files for consistency and correctness.
Run before committing changes.
"""

import json
import sys
from pathlib import Path
from collections import Counter

def load_json(filepath):
    """Load and validate JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error in {filepath}: {e}")
        return None
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        return None
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def validate_company_structure(company, index):
    """Validate individual company object structure."""
    errors = []
    warnings = []
    
    required_fields = ['id', 'name', 'slug', 'category', 'country', 'city', 'url', 'verification']
    
    for field in required_fields:
        if field not in company:
            errors.append(f"Company #{index}: Missing required field '{field}'")
    
    # Validate verification
    if 'verification' in company:
        if 'status' not in company['verification']:
            errors.append(f"Company #{index}: Missing verification.status")
        if 'sources' not in company['verification']:
            errors.append(f"Company #{index}: Missing verification.sources")
    
    # Validate URL format
    if 'url' in company and not company['url'].startswith('http'):
        warnings.append(f"Company #{index} ({company.get('name', '?')}): URL should start with http/https")
    
    # Check for empty values
    for field in ['name', 'slug', 'category']:
        if field in company and not company[field]:
            errors.append(f"Company #{index}: Field '{field}' is empty")
    
    return errors, warnings

def validate_master_file(filepath):
    """Validate data/companies.json master file."""
    print(f"\n📋 Validating: {filepath}")
    
    data = load_json(filepath)
    if not data:
        return False
    
    errors = []
    warnings = []
    
    # Check top-level structure
    if 'companies' not in data:
        errors.append("Missing 'companies' array")
        return False
    
    if 'count' not in data:
        errors.append("Missing 'count' field")
    
    # Validate count consistency
    actual_count = len(data['companies'])
    declared_count = data.get('count', 0)
    
    if actual_count != declared_count:
        errors.append(f"Count mismatch: declared={declared_count}, actual={actual_count}")
    
    # Validate each company
    ids = []
    slugs = []
    
    for idx, company in enumerate(data['companies'], 1):
        comp_errors, comp_warnings = validate_company_structure(company, idx)
        errors.extend(comp_errors)
        warnings.extend(comp_warnings)
        
        # Collect IDs and slugs for duplicate check
        if 'id' in company:
            ids.append(company['id'])
        if 'slug' in company:
            slugs.append(company['slug'])
    
    # Check for duplicates
    id_counts = Counter(ids)
    for id_val, count in id_counts.items():
        if count > 1:
            errors.append(f"Duplicate ID found: {id_val} (appears {count} times)")
    
    slug_counts = Counter(slugs)
    for slug, count in slug_counts.items():
        if count > 1:
            warnings.append(f"Duplicate slug found: {slug} (appears {count} times)")
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
    
    if warnings:
        print(f"⚠️  Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not errors and not warnings:
        print(f"✅ Validation passed: {actual_count} companies")
    
    return len(errors) == 0

def validate_derived_file(filepath, master_count):
    """Validate derived files (companies_all.json, etc.)."""
    print(f"\n📋 Validating: {filepath}")
    
    data = load_json(filepath)
    if not data:
        return False
    
    errors = []
    
    # Check count consistency
    if 'count' in data:
        if data['count'] != master_count:
            errors.append(f"Count mismatch with master: {data['count']} != {master_count}")
    
    # Check companies array
    if 'companies' in data:
        actual = len(data['companies'])
        if actual != master_count:
            errors.append(f"Array length mismatch: {actual} != {master_count}")
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} error(s):")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Validation passed")
    
    return len(errors) == 0

def validate_text_file(filepath, master_count):
    """Validate COMPANIES.txt consistency."""
    print(f"\n📋 Validating: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count numbered entries (1. 2. 3. etc.)
        import re
        entries = re.findall(r'^\d+\.\s+\w+', content, re.MULTILINE)
        actual_count = len(entries)
        
        if actual_count != master_count:
            print(f"❌ Entry count mismatch: {actual_count} != {master_count}")
            return False
        else:
            print(f"✅ Validation passed: {actual_count} entries")
            return True
    
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    """Run all validations."""
    print("=" * 60)
    print("🔍 CATALOG VALIDATION")
    print("=" * 60)
    
    all_passed = True
    
    # Validate master file
    master_path = Path('data/companies.json')
    master_valid = validate_master_file(master_path)
    all_passed = all_passed and master_valid
    
    if not master_valid:
        print("\n❌ Master file has errors. Fix before validating derived files.")
        sys.exit(1)
    
    # Get master count
    master_data = load_json(master_path)
    master_count = len(master_data['companies'])
    
    # Validate derived files
    derived_files = [
        Path('data/companies_all.json'),
    ]
    
    for filepath in derived_files:
        if filepath.exists():
            valid = validate_derived_file(filepath, master_count)
            all_passed = all_passed and valid
    
    # Validate COMPANIES.txt
    txt_path = Path('COMPANIES.txt')
    if txt_path.exists():
        valid = validate_text_file(txt_path, master_count)
        all_passed = all_passed and valid
    
    # Final report
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED")
        print(f"   Total companies: {master_count}")
        print("   Ready to commit!")
    else:
        print("❌ VALIDATION FAILED")
        print("   Please fix errors before committing.")
        sys.exit(1)
    print("=" * 60)

if __name__ == '__main__':
    main()
