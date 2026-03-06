"""
Verification Tasks - Complete Celery task implementations for background verification
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.workers.celery_app import app
from backend.core.database import SessionLocal, Business
from backend.services.verification_coordinator import VerificationCoordinator
from backend.services.trust_scorer import TrustScorer
from backend.core.config import settings

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def verify_single_business(self, business_id: int) -> Dict:
    """
    Verify a single business across all APIs
    
    Args:
        business_id: ID of business to verify
    
    Returns:
        Dictionary with verification results
    """
    db = SessionLocal()
    
    try:
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            logger.warning(f"Business {business_id} not found")
            return {"status": "not_found", "business_id": business_id}
        
        coordinator = VerificationCoordinator(
            two_gis_key=settings.TWOGIS_API_KEY,
            apify_token=settings.APIFY_TOKEN,
            google_key=settings.GOOGLE_PLACES_KEY
        )
        
        result = asyncio.run(
            coordinator.verify_business(business, db)
        )
        
        logger.info(f"Verified business {business_id}: {result.get('trust_score', 'N/A')}")
        
        return {
            "status": "success",
            "business_id": business_id,
            "trust_score": result.get("trust_score"),
            "verifications": result.get("verifications"),
            "verified_at": datetime.utcnow().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Error verifying business {business_id}: {str(exc)}", exc_info=True)
        
        try:
            raise self.retry(exc=exc)
        except Exception:
            return {
                "status": "failed",
                "business_id": business_id,
                "error": str(exc)
            }
    
    finally:
        db.close()


@app.task(bind=True)
def verify_all_businesses(self) -> Dict:
    """
    Verify all businesses in database
    Runs verification for entire catalog
    
    Returns:
        Summary of verification results
    """
    db = SessionLocal()
    
    try:
        businesses = db.query(Business).all()
        total = len(businesses)
        
        logger.info(f"Starting verification for {total} businesses")
        
        results = {
            "total": total,
            "verified": 0,
            "failed": 0,
            "by_category": {},
            "business_results": []
        }
        
        coordinator = VerificationCoordinator(
            two_gis_key=settings.TWOGIS_API_KEY,
            apify_token=settings.APIFY_TOKEN,
            google_key=settings.GOOGLE_PLACES_KEY
        )
        
        for idx, business in enumerate(businesses, 1):
            try:
                detail = asyncio.run(
                    coordinator.verify_business(business, db)
                )
                
                cat = business.category
                if cat not in results["by_category"]:
                    results["by_category"][cat] = {"verified": 0, "total": 0}
                
                results["by_category"][cat]["total"] += 1
                
                if any(v.get("verified") for v in detail.get("verifications", {}).values()):
                    results["verified"] += 1
                    results["by_category"][cat]["verified"] += 1
                
                results["business_results"].append({
                    "business_id": business.business_id,
                    "name": business.name,
                    "trust_score": detail.get("trust_score")
                })
                
                if idx % 10 == 0:
                    logger.info(f"Verified {idx}/{total} businesses")
            
            except Exception as e:
                logger.error(f"Error verifying {business.name}: {str(e)}")
                results["failed"] += 1
        
        logger.info(f"Verification complete: {results['verified']}/{total} verified")
        
        return results
    
    except Exception as exc:
        logger.error(f"Fatal error in verify_all_businesses: {str(exc)}", exc_info=True)
        return {"status": "failed", "error": str(exc)}
    
    finally:
        db.close()


@app.task(bind=True)
def verify_category(self, category: str, limit: Optional[int] = None) -> Dict:
    """
    Verify all businesses in a category
    
    Args:
        category: Business category
        limit: Maximum businesses to verify
    
    Returns:
        Verification summary for category
    """
    db = SessionLocal()
    
    try:
        query = db.query(Business).filter(Business.category == category)
        
        if limit:
            query = query.limit(limit)
        
        businesses = query.all()
        total = len(businesses)
        
        logger.info(f"Starting verification for {total} businesses in {category}")
        
        results = {
            "category": category,
            "total": total,
            "verified": 0,
            "failed": 0,
            "businesses": []
        }
        
        coordinator = VerificationCoordinator(
            two_gis_key=settings.TWOGIS_API_KEY,
            apify_token=settings.APIFY_TOKEN,
            google_key=settings.GOOGLE_PLACES_KEY
        )
        
        for business in businesses:
            try:
                detail = asyncio.run(
                    coordinator.verify_business(business, db)
                )
                
                if any(v.get("verified") for v in detail.get("verifications", {}).values()):
                    results["verified"] += 1
                
                results["businesses"].append({
                    "business_id": business.business_id,
                    "name": business.name,
                    "trust_score": detail.get("trust_score")
                })
            
            except Exception as e:
                logger.error(f"Error verifying {business.name}: {str(e)}")
                results["failed"] += 1
        
        logger.info(f"{category} verification complete: {results['verified']}/{total}")
        
        return results
    
    except Exception as exc:
        logger.error(f"Error in verify_category: {str(exc)}", exc_info=True)
        return {"status": "failed", "category": category, "error": str(exc)}
    
    finally:
        db.close()


@app.task(bind=True)
def recalculate_trust_scores(self) -> Dict:
    """
    Recalculate trust scores for all businesses
    Uses 6-factor algorithm
    
    Returns:
        Summary of updated scores
    """
    db = SessionLocal()
    
    try:
        businesses = db.query(Business).all()
        total = len(businesses)
        
        logger.info(f"Recalculating trust scores for {total} businesses")
        
        trust_scorer = TrustScorer()
        
        results = {
            "total": total,
            "updated": 0,
            "average_score": 0.0,
            "scores_by_category": {}
        }
        
        total_score = 0
        
        for business in businesses:
            try:
                new_score = trust_scorer.calculate_trust_score(
                    business=business,
                    db=db
                )
                
                business.trust_score = new_score
                total_score += new_score
                results["updated"] += 1
                
                cat = business.category
                if cat not in results["scores_by_category"]:
                    results["scores_by_category"][cat] = {
                        "count": 0,
                        "total_score": 0,
                        "average": 0
                    }
                
                results["scores_by_category"][cat]["count"] += 1
                results["scores_by_category"][cat]["total_score"] += new_score
            
            except Exception as e:
                logger.error(f"Error calculating score for {business.name}: {str(e)}")
        
        for cat in results["scores_by_category"]:
            cat_data = results["scores_by_category"][cat]
            cat_data["average"] = round(
                cat_data["total_score"] / cat_data["count"], 2
            )
        
        if results["updated"] > 0:
            results["average_score"] = round(total_score / results["updated"], 2)
        
        db.commit()
        
        logger.info(f"Trust scores updated - average: {results['average_score']}")
        
        return results
    
    except Exception as exc:
        logger.error(f"Error in recalculate_trust_scores: {str(exc)}", exc_info=True)
        db.rollback()
        return {"status": "failed", "error": str(exc)}
    
    finally:
        db.close()
