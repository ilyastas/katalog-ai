"""
Phase 3 Implementation - API Verifiers and OpenAI Integration
Updated: 2024
"""

# ✅ PHASE 3: INTEGRATIONS - COMPLETED

## Verifiers Created

### 1. 2ГИС Verifier
- **File**: `backend/verifiers/two_gis.py` (250+ lines)
- **Methods**:
  - `verify_business()` - Search and verify business existence
  - `get_business_details()` - Get full business information
  - `search_nearby()` - Find nearby businesses by coordinates
- **Features**:
  - Async HTTP client with httpx
  - Category extraction via rubrics
  - Contact information gathering
  - LocationPoint data for geocoding
  - Error handling with fallback

### 2. OLX Verifier
- **File**: `backend/verifiers/olx_verifier.py` (150+ lines)
- **Methods**:
  - `verify_seller()` - Check seller activity on OLX
  - `check_seller_ratings()` - Get seller ratings (extensible)
- **Features**:
  - Apify integration for OLX scraping
  - Active listing detection (30-day recency)
  - Seller credibility scoring
  - Graceful degradation if Apify not installed

### 3. Google Places Verifier
- **File**: `backend/verifiers/google_verifier.py` (280+ lines)
- **Methods**:
  - `search_business()` - Search by name/address/coordinates
  - `get_place_details()` - Get detailed place information
  - `verify_by_coordinates()` - Find businesses at location
- **Features**:
  - Text search and nearby search modes
  - Detailed place information (rating, reviews, hours)
  - Contact details extraction
  - Opening hours detection
  - Photo reference support

## OpenAI Integration

### 1. OpenAI Service
- **File**: `backend/services/openai_service.py` (380+ lines)
- **Components**:

#### Assistant Management
- `create_assistant()` - Create/retrieve ALIE assistant
  - Registers `search_verified_businesses` function
  - Sets up system instructions
  - Uses gpt-4-turbo-preview model

#### Function Calling
- `_get_business_search_function()` - Function definition
  - Parameters: query, category, city, verified_only, limit
  - Schema validation for OpenAI API
  - Supports Russian language queries

#### Function Processing
- `process_function_call()` - Execute function call from OpenAI
  - Delegates to RecommenderService
  - Returns formatted JSON response
  - Proper error handling

#### Thread Management (for multi-turn conversations)
- `create_thread()` - Start new conversation
- `send_message()` - Add message to thread
- `run_assistant()` - Execute assistant on thread
- `get_run_status()` - Check execution status
- `get_messages()` - Retrieve conversation history

### 2. Assistant Registration Script
- **File**: `backend/scripts/register_openai_assistant.py` (90+ lines)
- **How to use**:
  ```bash
  python backend/scripts/register_openai_assistant.py
  ```
- **Features**:
  - One-time setup
  - Checks for existing assistant (avoids duplicates)
  - Saves assistant ID to .env
  - Clear UI feedback

## Redis Caching Layer

### 1. Cache Decorators
- **File**: `backend/core/cache.py` (200+ lines)
- **Features**:
  - `@redis_cache()` decorator for async functions
  - Automatic key generation from function + args
  - TTL configuration
  - Graceful fallback if Redis unavailable

### 2. Cache Invalidation
- `CacheInvalidator` class
  - Pattern-based invalidation
  - Business-specific cache clearing
  - Recommendation cache clearing
  - Full cache flush

### 3. Cache TTL Constants
```python
CACHE_TTL = {
    "short": 300,          # 5 minutes
    "medium": 3600,        # 1 hour
    "long": 86400,         # 24 hours
    "business": 86400,     # Business details
    "recommendation": 3600, # Recommendations
    "nearby": 1800,        # Nearby search
    "statistics": 7200,    # Statistics
}
```

## Verifier Integration Module
- **File**: `backend/verifiers/__init__.py`
- **Exports**: TwoGISVerifier, OLXVerifier, GooglePlacesVerifier

---

## Configuration Required

### Environment Variables (in .env)

```env
# 2ГИС API
TWO_GIS_API_KEY=your_2gis_api_key

# OLX/Apify Integration
APIFY_TOKEN=your_apify_token

# Google Places
GOOGLE_PLACES_KEY=your_google_api_key

# OpenAI Integration  
OPENAI_API_KEY=your_openai_api_key
OPENAI_ASSISTANT_ID=generated_by_registration_script

# Redis Caching (already configured)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB_CACHE=0
```

---

## Database Schema Updates

Added fields to Business model:
- `external_links` - Dictionary with 2GIS, OLX URLs
- `verified_2gis` - Boolean flag
- `verified_olx` - Boolean flag
- `verified_google` - Boolean flag
- `google_rating` - Float (0-5)
- `google_reviews_count` - Integer
- `last_verification` - DateTime

Added VerificationLog table:
- Tracks all verification attempts
- Stores raw API responses
- Enables audit trail
- Supports verification scheduling

---

## What's Next (Phase 4)

1. **Complete Verification Tasks**
   - `backend/workers/tasks/verification_tasks.py`
   - Async verification for single and batch
   - Celery Beat scheduling

2. **API Endpoint Integration**
   - Add OpenAI chat endpoint
   - Thread management endpoints
   - Verification status endpoints

3. **Analytics Tasks**
   - Trust score recalculation
   - Lead value analysis
   - Recommendation performance metrics

---

## Testing Phase 3 Components

### Test Verifiers
```python
from backend.verifiers import TwoGISVerifier, GooglePlacesVerifier

# Test 2GIS
verifier = TwoGISVerifier(api_key)
result = await verifier.verify_business("Business Name")

# Test Google
g_verifier = GooglePlacesVerifier(api_key)
result = await g_verifier.search_business("Business Name")
```

### Test OpenAI Integration
```python
from backend.services.openai_service import OpenAIService

openai = OpenAIService(api_key)
assistant_id = openai.create_assistant()
thread_id = openai.create_thread()
```

---

**Status**: ✅ Phase 3 Verifiers and OpenAI Service - COMPLETE
**Files Created**: 7 files, ~1,500 lines of code
**Next**: Phase 4 - Celery Tasks and Analytics
