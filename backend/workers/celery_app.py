"""
Celery worker configuration for ALIE
Handles background tasks like verification and analytics
"""

from celery import Celery
from celery.schedules import crontab
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "alie",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard time limit
    task_soft_time_limit=25 * 60,  # 25 minute soft time limit
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # Results expire after 1 hour
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    # Daily verification of all businesses
    "verify-businesses-daily": {
        "task": "backend.workers.tasks.verification_tasks.verify_all_businesses",
        "schedule": crontab(hour=2, minute=0),  # 2 AM UTC daily
        "args": (),
        "options": {"queue": "default"}
    },
    
    # Calculate trust scores every 6 hours
    "calculate-trust-scores": {
        "task": "backend.workers.tasks.analytics_tasks.calculate_trust_scores",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        "args": (),
        "options": {"queue": "analytics"}
    },
    
    # Generate daily report
    "daily-report": {
        "task": "backend.workers.tasks.analytics_tasks.generate_daily_report",
        "schedule": crontab(hour=8, minute=0),  # 8 AM UTC
        "args": (),
        "options": {"queue": "analytics"}
    },
}

# Configure task routes for different queues
celery_app.conf.task_routes = {
    "backend.workers.tasks.verification_tasks.*": {"queue": "verification"},
    "backend.workers.tasks.analytics_tasks.*": {"queue": "analytics"},
    "backend.workers.tasks.tracking_tasks.*": {"queue": "tracking"},
}

logger.info(f"Celery configured with broker: {settings.CELERY_BROKER_URL}")
