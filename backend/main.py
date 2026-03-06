"""ALIE FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from datetime import datetime
import importlib
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.api.routes import api_router
from backend.core.config import settings
from backend.core.database import SessionLocal, init_db
from backend.models.schemas import ErrorResponse, HealthCheckResponse


logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize resources during startup and log shutdown."""
    logger.info("Starting ALIE API v%s", settings.APP_VERSION)
    logger.info("Environment: %s", settings.ENVIRONMENT)
    logger.info("Debug: %s", settings.DEBUG)

    try:
        init_db()
        logger.info("Database initialized")
    except Exception as exc:  # pragma: no cover
        logger.warning("Database initialization warning: %s", str(exc))

    yield
    logger.info("Shutting down ALIE API")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Attach short request id to each response for traceability."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return consistent 500 payload with request id context."""
    request_id = getattr(request.state, "request_id", None)
    logger.error("Unhandled exception [%s]: %s", request_id, str(exc), exc_info=True)
    payload = ErrorResponse(
        error="Internal server error",
        detail=str(exc) if settings.DEBUG else None,
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=payload.model_dump(exclude_none=True))


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["System"])
async def root():
    """Return basic API metadata and key endpoint links."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "docs": "/api/docs",
            "openapi": "/api/openapi.json",
            "health": "/health",
            "api": settings.API_V1_STR,
        },
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """Run lightweight health checks for API dependencies."""
    services = {
        "api": True,
        "neo4j": False,
        "postgres": False,
        "redis": False,
    }

    try:
        from backend.services.recommender import RecommenderService

        recommender = RecommenderService()
        recommender.close()
        services["neo4j"] = True
    except Exception as exc:
        logger.warning("Neo4j health check failed: %s", str(exc))

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        services["postgres"] = True
    except Exception as exc:
        logger.warning("PostgreSQL health check failed: %s", str(exc))

    try:
        redis_module = importlib.import_module("redis")
        redis_client = redis_module.Redis.from_url(
            settings.REDIS_URL, db=settings.REDIS_DB
        )
        redis_client.ping()
        services["redis"] = True
    except Exception as exc:
        logger.warning("Redis health check failed: %s", str(exc))

    status = "healthy" if all(services.values()) else "degraded"
    return HealthCheckResponse(
        status=status,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services,
    )


@app.get("/docs/endpoints", tags=["System"])
async def endpoints_documentation():
    """Return a concise endpoint catalog for external integrations."""
    return {
        "base_url": settings.CATALOG_BASE_URL,
        "version": settings.APP_VERSION,
        "endpoints": [
            {
                "path": f"{settings.API_V1_STR}/recommend/recommend",
                "method": "POST",
                "description": "Get AI-powered business recommendations",
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/business/{{business_id}}",
                "method": "GET",
                "description": "Get business details",
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/nearby",
                "method": "GET",
                "description": "Get nearby businesses",
            },
            {
                "path": f"{settings.API_V1_STR}/recommend/statistics/{{business_id}}",
                "method": "GET",
                "description": "Get lead statistics for a business",
            },
        ],
    }


def custom_openapi():
    """Generate custom OpenAPI schema with branding metadata."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.APP_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://ilyastas.github.io/katalog-ai/favicon.ico"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
