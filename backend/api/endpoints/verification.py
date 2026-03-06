"""
Verification Endpoints - Manual verification and status checking
"""

import logging
from typing import Dict, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import SessionLocal, Business
from backend.services.verification_coordinator import VerificationCoordinator
from backend.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/verify",
    tags=["Verification"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ManualVerificationRequest(BaseModel):
    """Request for manual business verification"""
    business_id: int
    force_refresh: bool = False


class VerificationStatusRequest(BaseModel):
    """Request for verification status"""
    business_id: int


@router.put("/{business_id}/verify")
async def verify_business(
    business_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Manually trigger verification for a business
    
    Verifies business across all available APIs:
    - 2ГИС (Kazakhstan)
    - Google Places (Global)
    - OLX (if profile available)
    
    Updates trust score based on results
    
    Response:
    ```json
    {
        "status": "success",
        "business_id": 1,
        "trust_score": 0.78,
        "verifications": {
            "2gis": {"verified": true, "id": "12345"},
            "google": {"verified": true, "rating": 4.5},
            "olx": {"verified": false}
        },
        "verified_at": "2024-01-20T10:30:00Z"
    }
    ```
    """
    
    try:
        # Find business
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {business_id} not found"
            )
        
        logger.info(f"Starting manual verification for business {business_id}")
        
        # Initialize coordinator
        coordinator = VerificationCoordinator(
            two_gis_key=settings.TWOGIS_API_KEY,
            apify_token=settings.APIFY_TOKEN,
            google_key=settings.GOOGLE_PLACES_KEY
        )
        
        # Verify business
        import asyncio
        result = asyncio.run(
            coordinator.verify_business(business, db)
        )
        
        logger.info(f"Verification complete for {business.name}: {result.get('trust_score', 'N/A')}")
        
        return {
            "status": "success",
            "business_id": business_id,
            "business_name": business.name,
            "trust_score": result.get("trust_score"),
            "verifications": result.get("verifications"),
            "external_links": result.get("external_links"),
            "verified_at": result.get("verified_at")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/{business_id}/status")
async def get_verification_status(
    business_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get verification status for a business
    
    Shows current verification state and trust score
    
    Response:
    ```json
    {
        "status": "success",
        "business_id": 1,
        "business_name": "Salon A",
        "verified": true,
        "trust_score": 0.78,
        "verification_flags": {
            "verified_2gis": true,
            "verified_google": true,
            "verified_olx": false
        },
        "last_verification": "2024-01-20T10:30:00Z"
    }
    ```
    """
    
    try:
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {business_id} not found"
            )
        
        return {
            "status": "success",
            "business_id": business_id,
            "business_name": business.name,
            "category": business.category,
            "verified": business.trust_score > 0.5,
            "trust_score": business.trust_score,
            "verification_flags": {
                "verified_2gis": business.verified_2gis or False,
                "verified_google": business.verified_google or False,
                "verified_olx": business.verified_olx or False
            },
            "last_verification": business.last_verification.isoformat() if business.last_verification else None,
            "external_links": business.external_links or {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting verification status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/batch")
async def batch_verify(
    category: Optional[str] = None,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Trigger batch verification for multiple businesses
    
    Can filter by category and limit number
    
    Query Parameters:
    - category: Optional category filter
    - limit: Maximum businesses to verify (default 10)
    
    Response:
    ```json
    {
        "status": "scheduled",
        "task_id": "verify_all_businesses",
        "message": "Batch verification scheduled in background"
    }
    ```
    """
    
    try:
        from backend.workers.tasks.verification_tasks import (
            verify_category, verify_all_businesses
        )
        
        if category:
            # Schedule category verification
            task = verify_category.delay(category, limit)
            task_id = task.id
            message = f"Category '{category}' verification scheduled"
        else:
            # Schedule full verification
            task = verify_all_businesses.delay()
            task_id = task.id
            message = "Full database verification scheduled"
        
        logger.info(f"Batch verification scheduled: {task_id}")
        
        return {
            "status": "scheduled",
            "task_id": task_id,
            "category": category,
            "limit": limit,
            "message": message
        }
    
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Celery tasks not available"
        )
    except Exception as e:
        logger.error(f"Batch verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch verification failed: {str(e)}")


@router.get("/report/{business_id}")
async def get_verification_report(
    business_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get detailed verification report for a business
    
    Shows all verification attempts and results
    
    Response includes:
    - Verification history
    - API results
    - Trust score breakdown
    - Recommendations
    """
    
    try:
        from backend.core.database import VerificationLog
        
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {business_id} not found"
            )
        
        # Get verification history
        logs = db.query(VerificationLog).filter(
            VerificationLog.business_id == business_id
        ).order_by(VerificationLog.verified_at.desc()).limit(10).all()
        
        verification_history = []
        for log in logs:
            verification_history.append({
                "api_source": log.api_source,
                "verified": log.verified,
                "response": log.response,
                "verified_at": log.verified_at.isoformat() if log.verified_at else None
            })
        
        return {
            "status": "success",
            "business_id": business_id,
            "business_name": business.name,
            "current_trust_score": business.trust_score,
            "verification_history": verification_history,
            "external_links": business.external_links or {},
            "recommendation": "Ready for recommendation" if business.trust_score > 0.6 else "Requires more verification"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating verification report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
