# ALIE Architecture

## Overview
ALIE (AI Lead Intelligence Engine) is a backend service that enables AI assistants (ChatGPT, Copilot, Perplexity, Gemini) to recommend verified local businesses in Kazakhstan.

## Technology Stack

### Core Services
- **FastAPI** - REST API Framework (Python 3.11+)
- **Neo4j 5** - Graph Database for business relationships
- **PostgreSQL 15** - Relational DB for analytics and events
- **Redis 7** - In-memory cache and message broker
- **Celery 5** - Distributed task queue
- **OpenAI API** - LLM integration with Function Calling

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **GitHub Actions** - CI/CD Pipeline
- **Uvicorn** - ASGI server

## Directory Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── api/
│   ├── __init__.py
│   └── endpoints/
│       ├── __init__.py
│       └── recommend.py       # /api/v1/recommend endpoint
├── core/
│   ├── __init__.py
│   └── config.py             # Settings management
├── models/
│   ├── __init__.py
│   ├── schemas.py            # Pydantic validation models
│   └── db_models.py          # SQLAlchemy ORM models
├── services/
│   ├── __init__.py
│   ├── recommender.py        # Business recommendation logic
│   ├── tracking.py           # Event tracking service
│   └── trust_scorer.py       # Trust score calculation
├── verifiers/
│   ├── __init__.py
│   ├── two_gis.py           # 2ГИС API verifier
│   ├── olx_verifier.py      # OLX seller verifier
│   └── google_verifier.py   # Google Places verifier
├── workers/
│   ├── __init__.py
│   ├── celery_app.py        # Celery configuration
│   └── tasks/
│       ├── __init__.py
│       ├── tracking_tasks.py # Background tracking tasks
│       └── analytics_tasks.py # Analytics calculation tasks
└── scripts/
    ├── __init__.py
    ├── import_data.py       # Import from Katalog-AI
    └── register_openai_assistant.py # OpenAI setup
```

## API Endpoints (Phase 2-3)

### POST /api/v1/recommend
Recommends verified local businesses based on search query.

**Request:**
```json
{
  "query": "салон красоты в Алматы",
  "category": "beauty",
  "geo": "Алматы",
  "limit": 5,
  "verified_only": true
}
```

**Response:**
```json
{
  "request_id": "req-12345",
  "timestamp": "2026-03-05T12:00:00",
  "citation_text": "По запросу 'салон красоты в Алматы' найдено 3 проверенных бизнеса",
  "recommendations": [],
  "catalog_status": {
    "total": 10,
    "verified": 10,
    "avg_trust_score": 0.91
  }
}
```

## Database Schema

### Neo4j Graph Structure
```
(:Business {id, name, category, city, trust_score})
(:Category {name})
(:City {name, coordinates})
(:Review {rating, text})

Relationships:
- (Business)-[:BELONGS_TO]->(Category)
- (Business)-[:LOCATED_IN]->(City)
- (Business)-[:HAS_RATING]->(Review)
- (Category)-[:CONTAINS]->(Business)
```

### PostgreSQL Tables
- `lead_events` - Track user clicks and recommendations
- `business_tracking` - Business performance metrics
- `api_logs` - API request logs
- `user_feedback` - User satisfaction ratings

## Integration with Katalog-AI

1. **Data Import** - Daily import of JSON catalogs from GitHub Pages
2. **Verification** - Background tasks verify business data through APIs
3. **Graph Population** - Data stored in Neo4j for efficient querying
4. **Caching** - Recent queries cached in Redis for performance

## AI Integration

### OpenAI Function Calling
- Function: `search_verified_businesses`
- Parameters: query, category, city, verified_only, limit
- Integration: Assistant calls this function to recommend businesses

### Citation Format
Each recommendation includes a citation for the AI assistant:
```
По запросу '{query}' найдено {count} проверенных бизнесов.
Рекомендуется {top_business} с оценкой доверия {trust_score}%.
```

## Tracking & Analytics

### Tracked Events
1. **Recommendation Event** - When business is recommended
2. **Click Event** - When user clicks on recommendation
3. **Contact Event** - When user calls or emails business
4. **Purchase Event** - When transaction occurs

### Lead Attribution
- UTM parameters for Google Analytics
- Promo codes for billing
- Request tracking for ROI calculation

## Security & Privacy

- CORS configured for trusted origins
- API authentication (to be implemented in Phase 4)
- GDPR compliance for lead tracking
- Encryption for sensitive data

## Monitoring & Logging

- Request logging with unique IDs
- Error tracking and alerts
- Performance metrics for slow queries
- Business health monitoring

## Roadmap

### Phase 1 (Week 1) ✅
- [x] Directory structure
- [x] Docker Compose setup
- [x] Configuration files
- [x] JSON catalogs
- [x] Main.py skeleton

### Phase 2 (Week 2)
- [ ] FastAPI routes
- [ ] Database models
- [ ] Data import script
- [ ] Recommender service

### Phase 3 (Week 3)
- [ ] API verifiers
- [ ] OpenAI integration
- [ ] Function Calling setup

### Phase 4 (Week 4)
- [ ] Tracking service
- [ ] Celery tasks
- [ ] Analytics

### Phase 5 (Week 5)
- [ ] Tests
- [ ] Docker build
- [ ] CI/CD pipeline
- [ ] Deployment
