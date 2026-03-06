# ALIE: Phase 1 - Foundation Ready! 🚀

This is the **Phase 1** completion for the **ALIE (AI Lead Intelligence Engine)** project - the backend platform that enables AI assistants to recommend verified local businesses in Kazakhstan.

## 📋 Phase 1: What's Included

### ✅ Complete Project Structure
- **Backend Architecture**: FastAPI-ready structure with separated concerns
- **Database Services**: Docker Compose with Neo4j, PostgreSQL, Redis, and Celery
- **JSON Catalogs**: 5 Schema.org compliant data files with 10 verified businesses
- **Configuration**: Environment management, Pydantic models, and Docker setup
- **AI Integration**: OpenAI Function Calling specification ready
- **Documentation**: Full architecture guide and checklist

### 📦 What You're Getting

```
ALIE/
├── data/
│   ├── index.json              ← Main manifest
│   └── catalog/
│       ├── beauty.json         (3 businesses)
│       ├── museums.json        (3 businesses)
│       ├── marketplaces.json   (3 businesses)
│       ├── offers.json         (6 services)
│       └── geo-index.json      (Geographic index)
├── backend/
│   ├── main.py                 ← FastAPI app
│   ├── core/config.py          ← Settings
│   ├── models/schemas.py       ← Pydantic models
│   ├── Dockerfile              ← Container build
│   └── requirements.txt         ← Dependencies
├── ai/
│   └── functions/
│       └── search_verified_businesses.json  ← OpenAI spec
├── docker-compose.yml          ← Services orchestration
├── .env.example                ← Configuration template
└── docs/
    ├── ARCHITECTURE.md         ← Full design
    └── PHASE1_CHECKLIST.md     ← Completion status
```

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose (or Python 3.11+ for local development)
- Git
- API Keys (get from existing Katalog-AI setup):
  - OpenAI API Key (for GPT-4)
  - 2ГИС API Key
  - Apify Token (for OLX scraping)
  - Google Places Key

### Option 1: Run with Docker Compose (Recommended)

```bash
# 1. Clone and navigate
cd katalog-ai

# 2. Copy environment template
cp .env.example .env

# 3. Add your API keys to .env
nano .env
# Set: OPENAI_API_KEY, TWOGIS_API_KEY, APIFY_TOKEN, GOOGLE_PLACES_KEY

# 4. Start all services
docker-compose up -d

# 5. Verify services are running
docker-compose ps

# 6. Check API health
curl http://localhost:8000/health
```

### Option 2: Run Locally (Development)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Create .env from template
cp .env.example .env

# 4. Set environment variable to use
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 5. Run FastAPI server
python -m uvicorn backend.main:app --reload

# Access API at http://localhost:8000
# Swagger docs at http://localhost:8000/api/docs
```

## 📊 Current Data

### Businesses in Catalog

| Category | City | Business | Status |
|----------|------|----------|--------|
| Beauty | Almaty | Beauty Premium Salon | ✅ Verified (2GIS, OLX, Google) |
| Beauty | Almaty | Glow Up Clinic | ✅ Verified (2GIS, Google) |
| Beauty | Almaty | Barbershop Gentleman | ✅ Verified (all APIs) |
| Culture | Almaty | Charyn Canyon Tours | ✅ Verified (2GIS, Google) |
| Culture | Almaty | Abaya Theatre | ✅ Verified (2GIS, Google) |
| Culture | Astana | National Museum KZ | ✅ Verified (2GIS, Google) |
| E-commerce | Almaty | TechHub KZ | ✅ Verified (2GIS, OLX) |
| E-commerce | Almaty | Fashion Elite | ✅ Verified (OLX) |
| E-commerce | Shymkent | Home Comfort | ✅ Verified (2GIS) |

**Total**: 10 verified businesses, Trust Score: 0.91 average

## 🔌 API Endpoints (Phase 2+)

Once Phase 2 is complete, you'll have:

```
POST /api/v1/recommend              ← Get business recommendations
GET /api/v1/business/{id}           ← Get business details
GET /api/v1/nearby                  ← Find businesses nearby (geo)
GET /health                         ← Health check
GET /api/docs                       ← Swagger UI
```

## 🗄️ Database Services

### Neo4j (Graph Database)
- **URL**: `bolt://localhost:7687`
- **User**: `neo4j`
- **Password**: `password123`
- **Browser**: http://localhost:7474
- **Purpose**: Store business relationships, categories, cities

### PostgreSQL
- **URL**: `postgresql://alie_user:postgres123@localhost:5432/alie_db`
- **Purpose**: Lead events, analytics, audience data

### Redis
- **URL**: `redis://localhost:6379`
- **Purpose**: Caching, session storage, Celery broker

## 📈 Next Phase: Phase 2 (Week 2)

In Phase 2, we'll implement:
- ✅ API endpoints with routing
- ✅ Database models (SQLAlchemy ORM)
- ✅ Data import scripts from Katalog-AI
- ✅ Recommender service with Neo4j queries
- ✅ Trust scoring algorithm

## 📚 Documentation

- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Full technical design
- **[PHASE1_CHECKLIST.md](./docs/PHASE1_CHECKLIST.md)** - Phase 1 completion status
- **[SETUP_API_KEYS.md](./docs/SETUP_API_KEYS.md)** - API key configuration (from Katalog-AI)

## 🔐 Credentials (Development Only!)

**⚠️ Change in production!**

```yaml
Neo4j:
  user: neo4j
  password: password123

PostgreSQL:
  user: alie_user
  password: postgres123
  database: alie_db

Redis:
  No auth (development)
```

## 🐛 Troubleshooting

### Services won't start
```bash
docker-compose down
docker volume prune
docker-compose up -d
```

### Check service logs
```bash
docker logs alie-neo4j
docker logs alie-postgres
docker logs alie-api
```

### Reset databases
```bash
docker-compose down -v
docker-compose up -d
```

## 🎯 Phase 1 Deliverables Completed

- ✅ Full project structure
- ✅ 5 JSON catalog files with Schema.org format
- ✅ Docker Compose with 6 services
- ✅ FastAPI skeleton with health checks
- ✅ Configuration management system
- ✅ Pydantic data models
- ✅ OpenAI Function Calling spec
- ✅ Complete architecture documentation

## 🚀 Ready for Phase 2!

All foundation is in place. We're ready to start implementing:
1. FastAPI endpoints
2. Database integration
3. Business logic (recommender service)
4. Data import from Katalog-AI

---

**Created**: 2026-03-05
**Status**: ✅ Phase 1 Complete
**Next**: Phase 2 - Backend Implementation
