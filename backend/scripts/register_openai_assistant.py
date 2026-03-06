"""
Script to register OpenAI Assistant with business search function
Run once during deployment: python backend/scripts/register_openai_assistant.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import asyncio
from backend.core.config import settings
from backend.services.openai_service import OpenAIService


async def register_assistant():
    """Register or retrieve OpenAI Assistant"""
    
    if not settings.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not set in .env file")
        print("Set the environment variable and try again")
        return None
    
    print("🔄 Initializing OpenAI Service...")
    openai_service = OpenAIService(settings.OPENAI_API_KEY)
    
    if not openai_service.client:
        print("❌ Failed to initialize OpenAI client")
        print("Make sure to install: pip install openai")
        return None
    
    print("🤖 Creating/retrieving assistant...")
    assistant_id = openai_service.create_assistant()
    
    if not assistant_id:
        print("❌ Failed to create assistant")
        return None
    
    print(f"✅ Assistant registered successfully!")
    print(f"   Assistant ID: {assistant_id}")
    print(f"   Name: ALIE Business Recommender")
    print(f"   Model: gpt-4-turbo-preview")
    print()
    print("📋 Function registered: search_verified_businesses")
    print("   - Searches verified local businesses in Kazakhstan")
    print("   - Filters by category, city, and trust score")
    print()
    print("💾 Store this Assistant ID in your .env file as:")
    print(f"   OPENAI_ASSISTANT_ID={assistant_id}")
    
    return assistant_id


def register_assistant_sync():
    """Synchronous wrapper for registration"""
    return asyncio.run(register_assistant())


if __name__ == "__main__":
    assistant_id = register_assistant_sync()
    
    if assistant_id:
        # Optionally save to .env
        env_file = Path(__file__).parent.parent.parent / ".env"
        
        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.read()
            
            # Check if already set
            if "OPENAI_ASSISTANT_ID=" not in env_content:
                with open(env_file, "a") as f:
                    f.write(f"\nOPENAI_ASSISTANT_ID={assistant_id}\n")
                print(f"\n✓ Updated .env file with assistant ID")
        
        sys.exit(0)
    else:
        sys.exit(1)
