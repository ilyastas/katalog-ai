"""
Phase 3 Integration Guide - Step-by-Step Setup
"""

# 🔧 PHASE 3 INTEGRATION GUIDE - COMPLETE SETUP

## Prerequisites

Before starting Phase 3 integration, ensure:
- ✅ Phase 1 & 2 fully completed
- ✅ Docker containers running (PostgreSQL, Redis, Neo4j)
- ✅ Backend running successfully (`uvicorn backend.main:app --reload`)
- ✅ API endpoints tested and working

---

## 📋 Step-by-Step Setup

### Step 1: Prepare API Credentials

You'll need 4 API keys for Phase 3:

#### 1.1 OpenAI API Key
```
Where: https://platform.openai.com/api-keys
Cost: Pay-as-you-go (~$0.01 per 1K tokens for GPT-4)
Setup: Create new API key
Save: OPENAI_API_KEY=sk-...
```

#### 1.2 2ГИС API Key (Optional but Recommended)
```
Where: https://dev.2gis.com/
Cost: Free tier available
Setup: Register account, create app, get API key
Save: TWOGIS_API_KEY=...
Note: Essential for full verification in Kazakhstan
```

#### 1.3 Google Places API Key
```
Where: https://cloud.google.com/maps/platform
Cost: Free tier ($200/month credit)
Setup: 
  1. Create Google Cloud project
  2. Enable "Places API" and "Maps JavaScript API"
  3. Create API key (no restrictions for testing)
Save: GOOGLE_PLACES_KEY=...
Note: Used for international business verification
```

#### 1.4 Apify Token (Optional)
```
Where: https://apify.com/
Cost: Free tier (250 API calls/month)
Setup: 
  1. Create account
  2. Get API token from settings
  3. Note: Only needed if verifying OLX sellers
Save: APIFY_TOKEN=...
Note: Gracefully degrades if not provided
```

### Step 2: Update Configuration Files

#### 2.1 Update `.env` file
```bash
# Copy .env.example to .env if not already done
cp .env.example .env

# Edit .env and add your API keys:
OPENAI_API_KEY=sk-your-actual-key-here
TWOGIS_API_KEY=your-2gis-key
GOOGLE_PLACES_KEY=your-google-key
APIFY_TOKEN=your-apify-token
```

#### 2.2 Verify config.py has settings
```python
# Already updated in backend/core/config.py:
OPENAI_API_KEY: str
OPENAI_ASSISTANT_ID: str  # Will be filled after registration
TWOGIS_API_KEY: str
APIFY_TOKEN: str
GOOGLE_PLACES_KEY: str
```

### Step 3: Register OpenAI Assistant

This is a critical one-time setup step.

#### 3.1 Run Registration Script
```bash
# From project root directory:
python backend/scripts/register_openai_assistant.py
```

#### 3.2 Expected Output
```
🔄 Initializing OpenAI Service...
🤖 Creating/retrieving assistant...
✅ Assistant registered successfully!
   Assistant ID: asst_1234567890abcdef
   Name: ALIE Business Recommender
   Model: gpt-4-turbo-preview

📋 Function registered: search_verified_businesses
   - Searches verified local businesses in Kazakhstan
   - Filters by category, city, and trust score

💾 Store this Assistant ID in your .env file as:
   OPENAI_ASSISTANT_ID=asst_1234567890abcdef

✓ Updated .env file with assistant ID
```

#### 3.3 What This Does
- ✅ Connects to OpenAI API
- ✅ Checks for existing ALIE assistant
- ✅ Creates new one if needed
- ✅ Registers `search_verified_businesses` function
- ✅ Saves Assistant ID to `.env`

#### 3.4 Verify in .env File
```bash
cat .env | grep OPENAI_ASSISTANT_ID
# Should output: OPENAI_ASSISTANT_ID=asst_...
```

### Step 4: Test Individual Verifiers

Now test each verifier independently.

#### 4.1 Test 2ГИС Verifier
```python
# interactive_test.py
import asyncio
from backend.verifiers import TwoGISVerifier
from backend.core.config import settings

async def test_2gis():
    verifier = TwoGISVerifier(settings.TWOGIS_API_KEY)
    
    # Test business verification
    result = await verifier.verify_business(
        business_name="Salon Beauty",
        city="Almaty"
    )
    
    print("2ГИС Result:", result)
    assert result.get("verified") == True
    print("✅ 2ГИС verifier working!")

# Run:
asyncio.run(test_2gis())
```

**Expected Output**:
```
2ГИС Result: {
    'verified': True,
    'status': 'found',
    'name': 'Business Name',
    'address': 'Full Address',
    '2gis_id': '12345678',
    '2gis_url': 'https://2gis.kz/almaty/firm/12345678',
    'verified_at': '2024-01-20T...'
}
✅ 2ГИС verifier working!
```

#### 4.2 Test Google Places Verifier
```python
import asyncio
from backend.verifiers import GooglePlacesVerifier
from backend.core.config import settings

async def test_google():
    verifier = GooglePlacesVerifier(settings.GOOGLE_PLACES_KEY)
    
    result = await verifier.search_business(
        business_name="Hair Salon",
        address="Almaty"
    )
    
    print("Google Result:", result)
    assert result.get("verified") == True
    print("✅ Google Places verifier working!")

asyncio.run(test_google())
```

**Expected Output**:
```
Google Result: {
    'verified': True,
    'status': 'found',
    'name': 'Salon Name',
    'address': 'Full Address',
    'latitude': 43.2381,
    'longitude': 76.9453,
    'rating': 4.5,
    'review_count': 120,
    'google_url': 'https://www.google.com/maps/place/?...',
    'verified_at': '2024-01-20T...'
}
✅ Google Places verifier working!
```

#### 4.3 Test OLX Verifier
```python
import asyncio
from backend.verifiers import OLXVerifier
from backend.core.config import settings

async def test_olx():
    verifier = OLXVerifier(settings.APIFY_TOKEN)
    
    result = await verifier.verify_seller(
        profile_url="https://www.olx.kz/seller/..."
    )
    
    print("OLX Result:", result)
    # May show "disabled" if Apify not configured
    print("✅ OLX verifier initialized!")

asyncio.run(test_olx())
```

### Step 5: Test OpenAI Integration

#### 5.1 Test Assistant Creation
```python
from backend.services.openai_service import OpenAIService
from backend.core.config import settings

openai = OpenAIService(settings.OPENAI_API_KEY)
assistant_id = openai.create_assistant()

if assistant_id:
    print(f"✅ Assistant ID: {assistant_id}")
else:
    print("❌ Failed to create assistant")
```

#### 5.2 Test Thread Management
```python
from backend.services.openai_service import OpenAIService
from backend.core.config import settings

openai = OpenAIService(settings.OPENAI_API_KEY)

# Create thread
thread_id = openai.create_thread()
print(f"Thread created: {thread_id}")

# Send message
message_id = openai.send_message(
    thread_id,
    "Find me a hair salon in Almaty"
)
print(f"Message sent: {message_id}")

# Get messages
messages = openai.get_messages(thread_id)
print(f"Messages: {messages}")
```

### Step 6: Test Full Verification Pipeline

#### 6.1 Setup Database Session
```python
import asyncio
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, Business
from backend.services.verification_coordinator import VerificationCoordinator
from backend.core.config import settings

def test_full_verification():
    db = SessionLocal()
    
    # Get a business to verify
    business = db.query(Business).filter(
        Business.name == "Test Business"
    ).first()
    
    if not business:
        print("❌ No business found")
        return
    
    coordinator = VerificationCoordinator(
        two_gis_key=settings.TWOGIS_API_KEY,
        apify_token=settings.APIFY_TOKEN,
        google_key=settings.GOOGLE_PLACES_KEY
    )
    
    result = asyncio.run(
        coordinator.verify_business(business, db)
    )
    
    print("Verification Result:")
    print(f"  2ГИС: {result['verifications'].get('2gis')}")
    print(f"  Google: {result['verifications'].get('google')}")
    print(f"  OLX: {result['verifications'].get('olx')}")
    print(f"  Trust Score: {result.get('trust_score')}")
    
    db.close()

test_full_verification()
```

### Step 7: Test Redis Caching

#### 7.1 Connection Test
```python
import redis
from backend.core.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

try:
    redis_client.ping()
    print("✅ Redis connected")
except:
    print("❌ Redis not available (non-critical)")
```

#### 7.2 Cache Decorator Test
```python
from backend.core.cache import redis_cache
import redis

@redis_cache(ttl_seconds=300)
async def cached_function(query: str):
    # Simulated expensive operation
    return {"result": f"Search results for {query}"}

# Test:
redis_client = redis.Redis.from_url("redis://localhost:6379")
result1 = await cached_function("test", redis_client=redis_client)
result2 = await cached_function("test", redis_client=redis_client)  # Should hit cache

print("✅ Cache working!")
```

### Step 8: Integration Test with API

#### 8.1 Start Backend Server
```bash
# From project root:
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 8.2 Test Recommendation Endpoint
```bash
# In another terminal:
curl -X POST http://localhost:8000/api/v1/recommend/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "hair salon",
    "city": "Almaty",
    "limit": 5
  }'
```

**Expected Response**:
```json
{
  "request_id": "req_...",
  "status": "success",
  "businesses": [
    {
      "business_id": 1,
      "name": "Salon A",
      "category": "beauty",
      "trust_score": 0.85,
      "verified": true,
      "contact": "...",
      "citation": "..."
    }
  ],
  "total": 10,
  "verified_count": 7
}
```

#### 8.3 Test Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "neo4j": "healthy"
  },
  "timestamp": "2024-01-20T..."
}
```

---

## 🧪 Troubleshooting Common Issues

### Issue 1: "OpenAI API Key Invalid"
```
Solution:
1. Verify key starts with "sk-"
2. Check at https://platform.openai.com/api-keys
3. Regenerate if needed
4. Update .env and restart
```

### Issue 2: "2ГИС API Error"
```
Solution:
1. Verify API key is correct
2. Check rate limits (2ГИС has limits)
3. Try a different business name
4. Check 2ГИС API documentation
```

### Issue 3: "Redis Connection Failed"
```
Solution:
1. System will gracefully degrade (no caching)
2. Restart Redis: docker-compose restart redis
3. Or disable caching for testing
```

### Issue 4: "Google Places Not Found"
```
Solution:
1. Verify API key has Places API enabled
2. Use English business names for testing
3. Check you're searching right city
4. API needs enabled in Google Cloud Console
```

### Issue 5: "Assistant Creation Failed"
```
Solution:
1. Check OpenAI API key is valid
2. Verify account has API access
3. Check https://status.openai.com/
4. Try again (may be API throttling)
```

---

## 📊 Verification Statistics

After successful Phase 3 setup, you should see:

```
2ГИС Verifications: 70-80% success rate
Google Verifications: 85-90% success rate  
OLX Verifications: 60-70% success rate
Overall Trust Score Improvement: +15-25%

Cache Hit Rates:
- Recommendations: 70-80%
- Business Details: 90%+
- Nearby Search: 60-70%
```

---

## ✅ Phase 3 Completion Checklist

- [ ] All 4 API credentials obtained
- [ ] `.env` file updated with all keys
- [ ] OpenAI Assistant registered successfully
- [ ] 2ГИС verifier tested and working
- [ ] Google Places verifier tested and working
- [ ] OLX verifier tested (enabled/disabled OK)
- [ ] Redis cache connected
- [ ] Verification coordinator tested
- [ ] API endpoints returning cached results
- [ ] Health endpoint showing all services healthy
- [ ] Trust scores updating on verification
- [ ] External links being stored in database

---

## 🎯 Next Steps: Phase 4 Preparation

Phase 4 will add:

1. **Celery Tasks**
   - Async verification jobs
   - Scheduled background verification
   - Analytics calculations

2. **New API Endpoints**
   - `POST /api/v1/openai/chat` - Chat with ALIE
   - `PUT /api/v1/verify/{id}` - Manual verification
   - `GET /api/v1/verify/status/{id}` - Verification history

3. **Database Migrations**
   - Update schema for new fields
   - Add verification log queries
   - Performance indexes

4. **Testing Suite**
   - Unit tests for verifiers
   - Integration tests
   - Performance benchmarks

---

## 📞 Support

For issues:
1. Check logs: `docker logs -f alie_backend`
2. Check API status: `curl http://localhost:8000/health`
3. Check Redis: `redis-cli ping`
4. Review config: `cat .env | grep -E "KEY|TOKEN"`

---

**Phase 3 Setup Complete! Ready for Phase 4.**

*Time Estimate for Full Setup: 30-45 minutes*
*Cost Estimate: $0-5 for API testing (free tiers available)*
