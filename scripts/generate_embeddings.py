#!/usr/bin/env python3
"""
Generate embeddings for all companies using OpenAI or Google AI.

This script reads company data from companies.json and generates
semantic embeddings via one of the supported providers:
    - OpenAI: text-embedding-3-small
    - Google AI (Gemini): models/gemini-embedding-001

Usage:
    python scripts/generate_embeddings.py --datafile data/companies.json --output data/embeddings.json
    python scripts/generate_embeddings.py --provider google

Requirements:
    - OPENAI_API_KEY (for OpenAI) or GOOGLE_AI_API_KEY (for Google AI)
    - pip install python-dotenv
    - pip install openai                # if provider=openai
    - pip install google-generativeai   # if provider=google

Security:
    - .env.local is in .gitignore (never committed)
    - GitHub Actions uses repository secrets
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

def mask_key(api_key):
    """Mask key for safe logging (first/last 6 chars only)."""
    if not api_key:
        return "***"
    if len(api_key) <= 14:
        return "***"
    return f"{api_key[:6]}***{api_key[-6:]}"


def get_google_ai_key():
    """Return Google AI key from unified env name."""
    return os.getenv('GOOGLE_AI_API_KEY')


def resolve_provider(preferred_provider):
    """Resolve provider based on flag and available keys."""
    if preferred_provider in ("openai", "google"):
        return preferred_provider

    # Auto mode: prefer Google if available (cheaper fallback when OpenAI billing is unavailable).
    if get_google_ai_key():
        return "google"
    if os.getenv('OPENAI_API_KEY'):
        return "openai"
    return None


def init_embedding_client(provider):
    """Initialize provider SDK client and return provider metadata."""
    if provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI package not installed. Install with: pip install openai"
            ) from exc

        client = OpenAI(api_key=api_key)
        return {
            "provider": "openai",
            "client": client,
            "model": "text-embedding-3-small",
            "generation_method": "OpenAI API",
            "masked_key": mask_key(api_key)
        }

    if provider == "google":
        api_key = get_google_ai_key()
        if not api_key:
            raise RuntimeError(
                "GOOGLE_AI_API_KEY not found"
            )

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise RuntimeError(
                "google-generativeai package not installed. Install with: pip install google-generativeai"
            ) from exc

        genai.configure(api_key=api_key)
        return {
            "provider": "google",
            "client": genai,
            "model": "models/gemini-embedding-001",
            "generation_method": "Google AI Gemini Embeddings API",
            "masked_key": mask_key(api_key)
        }

    raise RuntimeError(f"Unsupported provider: {provider}")


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


def get_embedding(client_ctx, text):
    """
    Get embedding vector from the selected provider.
    
    Args:
        client_ctx: Provider context with initialized client/model
        text: Text to embed
    
    Returns:
        List of floats representing the embedding vector
    """
    try:
        provider = client_ctx["provider"]

        if provider == "openai":
            response = client_ctx["client"].embeddings.create(
                input=text,
                model=client_ctx["model"]
            )
            return response.data[0].embedding

        if provider == "google":
            response = client_ctx["client"].embed_content(
                model=client_ctx["model"],
                content=text,
                task_type="retrieval_document"
            )
            if isinstance(response, dict):
                embedding = response.get("embedding")
            else:
                embedding = getattr(response, "embedding", None)

            if embedding is None:
                raise RuntimeError("Google AI response does not contain 'embedding'")

            return embedding

        raise RuntimeError(f"Unsupported provider: {provider}")

    except Exception as e:
        print(f"ERROR: Failed to generate embedding: {e}")
        raise


def generate_embeddings(datafile, output_file=None, provider="auto"):
    """
    Generate embeddings for all companies.
    
    Args:
        datafile: Path to companies.json
        output_file: Path to save embeddings.json (default: public/embeddings.json)
        provider: Embedding provider (auto|openai|google)
    """
    resolved_provider = resolve_provider(provider)
    if not resolved_provider:
        print("❌ ERROR: No embedding API key found!")
        print("\n📝 Setup instructions:")
        print("  1. Choose provider:")
        print("     - OpenAI key: OPENAI_API_KEY=sk-proj-...")
        print("     - Google AI key: GOOGLE_AI_API_KEY=AIza...")
        print("  2. Local development:")
        print("     - Create .env.local file (in .gitignore)")
        print("     - Add one of the keys above")
        print("  3. GitHub Actions (CI/CD):")
        print("     - Go: https://github.com/ilyastas/katalog-ai/settings/secrets/actions")
        print("     - Add secret: OPENAI_API_KEY or GOOGLE_AI_API_KEY")
        print("  4. Terminal (temporary):")
        print("     - export OPENAI_API_KEY='sk-...' OR")
        print("     - export GOOGLE_AI_API_KEY='AIza...'")
        sys.exit(1)

    # Initialize selected provider client
    try:
        client_ctx = init_embedding_client(resolved_provider)
    except Exception as e:
        print(f"❌ Failed to initialize embedding client: {e}")
        sys.exit(1)

    print(f"🔌 Provider: {client_ctx['provider']}")
    print(f"🧠 Model: {client_ctx['model']}")
    print(f"🔑 Using API key: {client_ctx['masked_key']}")

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
            "embedding_provider": client_ctx["provider"],
            "embedding_model": client_ctx["model"],
            "vector_dimension": None,
            "total_embeddings": len(companies),
            "update_frequency": "weekly",
            "generation_method": client_ctx["generation_method"]
        },
        "embeddings": []
    }

    print(f"🔄 Generating embeddings with {client_ctx['model']}...")
    failed_companies = []

    for idx, company in enumerate(companies, 1):
        try:
            # Generate text for embedding
            embed_text = generate_text_for_embedding(company)
            
            # Get embedding from selected provider
            embedding_vector = get_embedding(client_ctx, embed_text)

            if embeddings_data["metadata"]["vector_dimension"] is None:
                embeddings_data["metadata"]["vector_dimension"] = len(embedding_vector)

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

        expected_dimension = data.get('metadata', {}).get('vector_dimension')

        # Validate each embedding
        for i, embedding in enumerate(data['embeddings']):
            assert 'company_id' in embedding, f"Embedding {i}: missing company_id"
            assert 'embedding' in embedding, f"Embedding {i}: missing embedding vector"
            vector = embedding['embedding']
            assert isinstance(vector, list), f"Embedding {i}: vector must be a list"
            assert vector, f"Embedding {i}: vector is empty"

            if expected_dimension is None:
                expected_dimension = len(vector)
            assert len(vector) == expected_dimension, f"Embedding {i}: wrong vector dimension"

        print(f"✅ Validation passed: {len(data['embeddings'])} valid embeddings")
        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate embeddings for companies using OpenAI or Google AI'
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
    parser.add_argument(
        '--provider',
        choices=['auto', 'openai', 'google'],
        default='auto',
        help='Embedding provider (default: auto)'
    )

    args = parser.parse_args()

    if args.validate:
        print(f"🔍 Validating {args.output}...")
        validate_embeddings(args.output)
        return

    print("🚀 Katalog-AI: Embedding Generation")
    print("=" * 50)

    # Generate embeddings
    success = generate_embeddings(args.datafile, args.output, provider=args.provider)

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
