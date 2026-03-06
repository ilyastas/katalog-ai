#!/usr/bin/env python3
"""
Generate embeddings for all companies using OpenAI API.

This script reads company data from companies.json and generates
semantic embeddings using OpenAI's text-embedding-3-small model.

Usage:
    python scripts/generate_embeddings.py --datafile data/companies.json --output data/embeddings.json

Requirements:
    - OPENAI_API_KEY environment variable set (via .env.local or GitHub Secrets)
    - pip install openai python-dotenv

Security:
    - .env.local is in .gitignore (never committed)
    - GitHub Actions uses ${{ secrets.OPENAI_API_KEY }}
    - Never paste API keys into code or public files
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load environment variables from .env.local or .env
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local', override=True)  # Local dev secrets
    load_dotenv('.env', override=False)        # Default values
except ImportError:
    print("Note: python-dotenv not installed. Skipping .env loading.")

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: OpenAI package not installed. Install with: pip install openai")
    sys.exit(1)


def load_companies(datafile):
    """Load company data from JSON file."""
    try:
        with open(datafile, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('companies', [])
    except FileNotFoundError:
        print(f"ERROR: Company data file not found: {datafile}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in {datafile}")
        sys.exit(1)


def generate_text_for_embedding(company):
    """Generate embedding text from company data."""
    parts = [
        company.get('name', ''),
        company.get('service', ''),
        company.get('description', ''),
        company.get('category', ''),
        ' '.join(company.get('services', [])),
    ]
    return ' '.join(filter(None, parts))


def get_embedding(client, text, model="text-embedding-3-small"):
    """
    Get embedding from OpenAI API.
    
    Args:
        client: OpenAI client instance
        text: Text to embed
        model: Embedding model to use
    
    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"ERROR: Failed to generate embedding: {e}")
        raise


def generate_embeddings(datafile, output_file=None, batch_size=20):
    """
    Generate embeddings for all companies.
    
    Args:
        datafile: Path to companies.json
        output_file: Path to save embeddings.json (default: public/embeddings.json)
        batch_size: Number of companies per API batch
    """
    # Validate API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found!")
        print("\n📝 Setup instructions:")
        print("  1. Get API key from: https://platform.openai.com/api-keys")
        print("  2. Local development:")
        print("     - Create .env.local file (in .gitignore)")
        print("     - Add: OPENAI_API_KEY=sk-proj-...")
        print("  3. GitHub Actions (CI/CD):")
        print("     - Go: https://github.com/ilyastas/katalog-ai/settings/secrets/actions")
        print("     - Add secret: OPENAI_API_KEY")
        print("  4. Terminal (temporary):")
        print("     - export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    # Mask key for logging (show only first/last 10 chars)
    masked_key = api_key[:10] + "***" + api_key[-10:] if len(api_key) > 20 else "***"
    print(f"🔑 Using API key: {masked_key}")

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        sys.exit(1)

    # Load companies
    companies = load_companies(datafile)
    if not companies:
        print("ERROR: No companies found in datafile")
        sys.exit(1)

    print(f"📊 Loaded {len(companies)} companies from {datafile}")

    # Set default output path
    if not output_file:
        output_file = 'data/embeddings.json'

    # Generate embeddings
    embeddings_data = {
        "dataset": "katalog-ai-embeddings",
        "version": "1.0.0",
        "type": "Vector Embeddings Storage",
        "description": "Pre-computed embeddings for all companies for semantic search",
        "metadata": {
            "created": datetime.utcnow().isoformat() + "Z",
            "embedding_model": "text-embedding-3-small",
            "vector_dimension": 1536,
            "total_embeddings": len(companies),
            "update_frequency": "weekly",
            "generation_method": "OpenAI API"
        },
        "embeddings": []
    }

    print(f"🔄 Generating embeddings with text-embedding-3-small...")
    failed_companies = []

    for idx, company in enumerate(companies, 1):
        try:
            # Generate text for embedding
            embed_text = generate_text_for_embedding(company)
            
            # Get embedding from OpenAI API
            embedding_vector = get_embedding(client, embed_text)

            # Store embedding data
            embedding_record = {
                "company_id": company.get('id'),
                "company_name": company.get('name'),
                "embedding": embedding_vector,
                "source_text": embed_text[:200],  # First 200 chars for reference
                "entity_type": "LocalBusiness",
                "fields_embedded": ["name", "service", "description", "category", "services"],
                "embedding_timestamp": datetime.utcnow().isoformat() + "Z",
                "quality_score": 0.95,  # Default quality for API-generated embeddings
                "metadata": {
                    "service": company.get('service'),
                    "category": company.get('category'),
                    "city": company.get('city'),
                    "trust_score": company.get('trust_score'),
                    "rating": company.get('rating'),
                    "reviews_count": company.get('reviews_count'),
                    "languages": company.get('languages', [])
                }
            }

            embeddings_data["embeddings"].append(embedding_record)

            # Progress indicator
            progress = f"[{idx}/{len(companies)}]"
            print(f"✅ {progress} {company.get('name')}")

        except Exception as e:
            failed_companies.append((company.get('id'), str(e)))
            print(f"❌ {company.get('id')}: {e}")

    # Save embeddings to file
    try:
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Embeddings saved to {output_file}")
        print(f"📊 Total embeddings: {len(embeddings_data['embeddings'])}")

        if failed_companies:
            print(f"\n⚠️  Failed to generate embeddings for {len(failed_companies)} companies:")
            for company_id, error in failed_companies:
                print(f"   - {company_id}: {error}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to save embeddings: {e}")
        return False


def validate_embeddings(embeddings_file):
    """Validate embeddings file structure."""
    try:
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check required fields
        assert 'embeddings' in data, "Missing 'embeddings' field"
        assert isinstance(data['embeddings'], list), "'embeddings' must be a list"

        # Validate each embedding
        for i, embedding in enumerate(data['embeddings']):
            assert 'company_id' in embedding, f"Embedding {i}: missing company_id"
            assert 'embedding' in embedding, f"Embedding {i}: missing embedding vector"
            assert len(embedding['embedding']) == 1536, f"Embedding {i}: wrong vector dimension"

        print(f"✅ Validation passed: {len(data['embeddings'])} valid embeddings")
        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate embeddings for companies using OpenAI API'
    )
    parser.add_argument(
        '--datafile',
        default='data/companies.json',
        help='Path to companies.json (default: data/companies.json)'
    )
    parser.add_argument(
        '--output',
        default='data/embeddings.json',
        help='Path to save embeddings.json (default: data/embeddings.json)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate existing embeddings file'
    )

    args = parser.parse_args()

    if args.validate:
        print(f"🔍 Validating {args.output}...")
        validate_embeddings(args.output)
        return

    print("🚀 Katalog-AI: Embedding Generation")
    print("=" * 50)

    # Generate embeddings
    success = generate_embeddings(args.datafile, args.output)

    if success:
        # Validate generated embeddings
        print("\n🔍 Validating generated embeddings...")
        validate_embeddings(args.output)
        print("\n✨ Complete!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
