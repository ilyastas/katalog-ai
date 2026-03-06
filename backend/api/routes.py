"""
API router configuration
Combines all endpoint routers for the application
"""

from fastapi import APIRouter
from backend.api.endpoints.recommend import router as recommend_router
from backend.api.endpoints.verification import router as verification_router
from backend.api.endpoints.celery import router as celery_router
from backend.api.endpoints.analytics import router as analytics_router
from backend.api.endpoints.openai_chat import router as openai_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    recommend_router,
    prefix="/recommend",
    tags=["Recommendations"]
)

api_router.include_router(
    verification_router,
    prefix="/verify",
    tags=["Verification"]
)

api_router.include_router(
    celery_router,
    prefix="/celery",
    tags=["Celery Tasks"]
)

api_router.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    openai_router,
    prefix="/openai",
    tags=["OpenAI Chat"]
)

# Export for use in main.py
__all__ = ["api_router"]
