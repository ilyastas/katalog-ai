"""
ALIE - AI Lead Intelligence Engine
FastAPI application initialization and configuration
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from backend.core.config import settings
from backend.models.schemas import ErrorResponse, HealthCheckResponse
from backend.api.routes import api_router
from backend.core.database import init_db

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage startup and shutdown events
    """
    # Startup
    logger.info(f"🚀 Starting ALIE API v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug: {settings.DEBUG}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization warning: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ALIE API")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """
    Add unique request ID to all requests
    """
    import uuid
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
    # Check service connectivity
    services = {
        "api": True,
        "neo4j": False,
        "postgres": False,
        "redis": False
    }
    
    # Check Neo4j
    try:
        from backend.services.recommender import RecommenderService
        recommender = RecommenderService()
        recommender.close()
        services["neo4j"] = True
    except Exception as e:
        logger.warning(f"Neo4j health check failed: {str(e)}")
    
    # Check PostgreSQL
    try:
        from backend.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        services["postgres"] = True
    except Exception as e:
        logger.warning(f"PostgreSQL health check failed: {str(e)}")
    
  Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns API information
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "openapi": "/api/openapi.json",
            "health": "/health",
            "recommend": f"{settings.API_V1_STR}/recommend/recommend",
            "business_details": f"{settings.API_V1_STR}/recommend/business/{{business_id}}",
            "nearby": f"{settings.API_V1_STR}/recommend/nearby",
            "statistics": f"{settings.API_V1_STR}/recommend/statistics/{{business_id}}"
        } all(services.values()) else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services"/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services={
            "api": True,
            "neo4j": True,
            "postgres": True,
            "redis": True
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint that returns API information
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "openapi": "/api/openapi.json",
        "health": "/health"
    }


# Custom OpenAPI schema
def custom_openapi():
    """
    Generate custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.APP_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
  Additional documentation
@app.get("/docs/endpoints")
async def endpoints_documentation():
    """
    Detailed endpoint documentation
    """
    return {
        "base_url": settings.CATALOG_BASE_URL,
        "version": settings.APP_VERSION,
        "endpoints": [
            {
                "path": f"{settings.API_V1_STR}/recommend/recommend",
                "method": "POST",
                "description": "Get AI-powered business recommendations",
                "example": {
                    "query": "салон красоты в Алматы",
                    "category": "beauty",
                    "geo": "Алматы",
                    "limit": 5
                }
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/business/{{business_id}}",
                "method": "GET",
                "description": "Get business details"
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/nearby",
                "method": "GET",
                "description": "Get nearby businesses (geo search)",
                "params": ["latitude", "longitude", "radius_km", "limit"]
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/statistics/{{business_id}}",
                "method": "GET",
                "description": "Get lead statistics for business"
            }
        ]
    }
    return app.openapi_schema


app.openapi = custom_openapi


# Import and include routers
# Note: These will be created in Phase 2
# from backend.api.endpoints import recommend_router
# app.include_router(recommend_router, prefix=settings.API_V1_STR, tags=["Recommendations"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
