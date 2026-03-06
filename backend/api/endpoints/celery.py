"""
Celery Task Management Endpoints - Async job execution and monitoring
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import SessionLocal
from backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/celery",
    tags=["Celery Tasks"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/verify/single/{business_id}")
async def verify_single_business(
    business_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Trigger verification for a single business in background
    
    Returns task ID for tracking progress
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "business_id": 1,
        "status": "pending",
        "message": "Verification started"
    }
    ```
    """
    
    try:
        # Check business exists
        from backend.core.database import Business
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {business_id} not found"
            )
        
        # Import and trigger Celery task
        from backend.workers.tasks.verification_tasks import verify_single_business
        
        task = verify_single_business.delay(business_id)
        
        logger.info(f"Verification task started for business {business_id}: {task.id}")
        
        return {
            "task_id": task.id,
            "business_id": business_id,
            "business_name": business.name,
            "status": "pending",
            "message": "Verification started in background",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(status_code=500, detail="Celery not configured")
    except Exception as e:
        logger.error(f"Failed to schedule verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.post("/verify/all")
async def verify_all_businesses(db: Session = Depends(get_db)) -> Dict:
    """
    Trigger batch verification for all businesses
    
    Processes entire catalog in background
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "total_businesses": 250,
        "status": "pending",
        "estimated_duration_minutes": 15
    }
    ```
    """
    
    try:
        from backend.core.database import Business
        from backend.workers.tasks.verification_tasks import verify_all_businesses
        
        # Get business count
        total_count = db.query(Business).count()
        
        if total_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No businesses found to verify"
            )
        
        # Trigger task
        task = verify_all_businesses.delay()
        
        # Rough estimate: 10 seconds per business
        estimated_duration = (total_count * 10) // 60
        
        logger.info(f"Full verification task started: {task.id} ({total_count} businesses)")
        
        return {
            "task_id": task.id,
            "total_businesses": total_count,
            "status": "pending",
            "estimated_duration_minutes": max(1, estimated_duration),
            "message": f"Verification of {total_count} businesses started",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule batch verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.post("/verify/category/{category}")
async def verify_category(
    category: str,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Trigger verification for a specific category
    
    Query Parameters:
    - limit: Optional limit on number of businesses (for testing)
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "category": "hair_salon",
        "businesses_to_verify": 45,
        "status": "pending"
    }
    ```
    """
    
    try:
        from backend.core.database import Business
        from backend.workers.tasks.verification_tasks import verify_category as verify_cat_task
        
        # Get category count
        count = db.query(Business).filter(
            Business.category == category
        ).count()
        
        if count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No businesses found in category '{category}'"
            )
        
        # Trigger task
        task = verify_cat_task.delay(category, limit)
        
        logger.info(f"Category verification started for '{category}': {task.id} ({count} businesses)")
        
        return {
            "task_id": task.id,
            "category": category,
            "businesses_to_verify": min(count, limit) if limit else count,
            "status": "pending",
            "message": f"Verification of {category} category started",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule category verification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.post("/recalculate-scores")
async def recalculate_trust_scores(db: Session = Depends(get_db)) -> Dict:
    """
    Trigger recalculation of all trust scores
    
    Uses 6-factor algorithm:
    - 2ГИС verification (25%)
    - OLX verification (15%)
    - Google verification (25%)
    - Business rating (15%)
    - Click-through rate (10%)
    - Recency (10%)
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "businesses_to_process": 250,
        "status": "pending"
    }
    ```
    """
    
    try:
        from backend.core.database import Business
        from backend.workers.tasks.verification_tasks import recalculate_trust_scores
        
        count = db.query(Business).count()
        
        if count == 0:
            raise HTTPException(
                status_code=400,
                detail="No businesses found"
            )
        
        # Trigger task
        task = recalculate_trust_scores.delay()
        
        logger.info(f"Trust score recalculation started: {task.id} ({count} businesses)")
        
        return {
            "task_id": task.id,
            "businesses_to_process": count,
            "status": "pending",
            "algorithm": "6-factor weighted average",
            "weights": {
                "2gis": 0.25,
                "olx": 0.15,
                "google": 0.25,
                "rating": 0.15,
                "ctr": 0.10,
                "recency": 0.10
            },
            "message": "Trust score recalculation started",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule trust score recalculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict:
    """
    Get status of a Celery task
    
    Returns real-time status and results
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "status": "SUCCESS",
        "progress": 100,
        "result": {
            "total": 250,
            "verified": 245,
            "failed": 5
        },
        "completed_at": "2024-01-20T10:45:00Z"
    }
    ```
    """
    
    try:
        from celery.result import AsyncResult
        from backend.core.cache import get_redis_client
        
        # Get task from Celery
        task = AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": task.status,
            "progress": 0
        }
        
        # Add progress/result based on status
        if task.status == "PENDING":
            response["progress"] = 0
            response["message"] = "Task pending..."
        
        elif task.status == "PROGRESS":
            response["progress"] = task.info.get("current", 0) if task.info else 0
            response["total"] = task.info.get("total", 0) if task.info else 0
            response["message"] = task.info.get("status", "Processing...") if task.info else "Processing..."
        
        elif task.status == "SUCCESS":
            response["progress"] = 100
            response["result"] = task.result
            response["completed_at"] = datetime.utcnow().isoformat()
        
        elif task.status == "FAILURE":
            response["error"] = str(task.info)
            response["completed_at"] = datetime.utcnow().isoformat()
        
        elif task.status == "RETRY":
            response["progress"] = 0
            response["message"] = f"Task retrying... Next attempt soon"
        
        logger.info(f"Task status check: {task_id} -> {task.status}")
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.post("/analytics/daily")
async def calculate_daily_statistics(db: Session = Depends(get_db)) -> Dict:
    """
    Trigger daily statistics calculation
    
    Aggregates previous day's events
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "date": "2024-01-19",
        "status": "pending"
    }
    ```
    """
    
    try:
        from backend.workers.tasks.analytics_tasks import calculate_daily_statistics
        
        task = calculate_daily_statistics.delay()
        
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        
        logger.info(f"Daily statistics calculation started: {task.id}")
        
        return {
            "task_id": task.id,
            "date": yesterday.isoformat(),
            "status": "pending",
            "message": f"Daily statistics for {yesterday} scheduled",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except Exception as e:
        logger.error(f"Failed to schedule daily statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.post("/analytics/monthly")
async def calculate_monthly_report(db: Session = Depends(get_db)) -> Dict:
    """
    Trigger monthly report generation
    
    Calculates 30-day rolling metrics
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "status": "pending",
        "period_days": 30
    }
    ```
    """
    
    try:
        from backend.workers.tasks.analytics_tasks import calculate_monthly_report
        
        task = calculate_monthly_report.delay()
        
        logger.info(f"Monthly report generation started: {task.id}")
        
        return {
            "task_id": task.id,
            "status": "pending",
            "period_days": 30,
            "message": "Monthly report generation scheduled",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except Exception as e:
        logger.error(f"Failed to schedule monthly report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_logs(
    days_to_keep: int = 90,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Trigger cleanup of old logs
    
    Deletes API logs older than specified days
    
    Query Parameters:
    - days_to_keep: Number of days to retain (default 90)
    
    Response:
    ```json
    {
        "task_id": "a1b2c3d4-...",
        "days_to_keep": 90,
        "status": "pending"
    }
    ```
    """
    
    try:
        from backend.workers.tasks.analytics_tasks import cleanup_old_logs as cleanup_task
        
        if days_to_keep < 7:
            raise HTTPException(
                status_code=400,
                detail="Minimum retention period is 7 days"
            )
        
        if days_to_keep > 365:
            raise HTTPException(
                status_code=400,
                detail="Maximum retention period is 365 days"
            )
        
        task = cleanup_task.delay(days_to_keep)
        
        logger.info(f"Log cleanup scheduled: {task.id} (keeping {days_to_keep} days)")
        
        return {
            "task_id": task.id,
            "days_to_keep": days_to_keep,
            "status": "pending",
            "message": f"Log cleanup for records older than {days_to_keep} days scheduled",
            "check_status_url": f"/api/v1/celery/tasks/{task.id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to schedule cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to schedule task: {str(e)}")


@router.get("/tasks/summary")
async def get_tasks_summary() -> Dict:
    """
    Get summary of all active and recent tasks
    
    Response:
    ```json
    {
        "active_tasks": 3,
        "completed_tasks": 45,
        "failed_tasks": 2,
        "active": [
            {
                "task_id": "a1b2c3d4-...",
                "type": "verify_all_businesses",
                "status": "PROGRESS",
                "progress": 65
            }
        ]
    }
    ```
    """
    
    try:
        # This would connect to Celery's inspect API
        from celery import Celery
        from backend.workers.celery_app import app as celery_app
        
        inspect = celery_app.control.inspect()
        
        active = inspect.active()
        reserved = inspect.reserved()
        
        active_tasks = {}
        if active:
            for worker, tasks in active.items():
                for task in tasks:
                    active_tasks[task['id']] = {
                        "task_id": task['id'],
                        "type": task['name'],
                        "worker": worker,
                        "args": task.get('args'),
                        "started": task.get('time_start')
                    }
        
        logger.info(f"Tasks summary: {len(active_tasks)} active tasks")
        
        return {
            "active_tasks": len(active_tasks),
            "active": list(active_tasks.values()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting tasks summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tasks summary: {str(e)}")
