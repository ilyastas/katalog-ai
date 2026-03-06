"""
Trust scoring service for calculating business reliability scores
"""

from sqlalchemy.orm import Session
from backend.core.database import Business, LeadEvent
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TrustScorer:
    """
    Calculate trust scores based on verification and engagement metrics
    """
    
    def __init__(self):
        self.weights = {
            "2gis_verification": 0.25,
            "olx_verification": 0.15,
            "google_verification": 0.25,
            "rating": 0.15,
            "click_through_rate": 0.10,
            "recency": 0.10
        }
    
    def calculate_trust_score(self, business: Business, db: Session) -> float:
        """
        Calculate overall trust score for a business
        
        Factors:
        - Verification through multiple APIs (0-0.65)
        - User ratings (0-0.15)
        - Click-through rate (0-0.10)
        - Recency of verification (0-0.10)
        """
        
        score = 0.0
        
        # Verification scores (0.65 total)
        verification_score = 0.0
        if business.verified_by_2gis:
            verification_score += 0.25
        if business.verified_by_olx:
            verification_score += 0.15
        if business.verified_by_google:
            verification_score += 0.25
        
        score += verification_score
        
        # Rating score (0.15 total)
        if business.rating and business.rating_count > 0:
            # Normalize rating from 0-5 to 0-0.15
            rating_normalized = (business.rating / 5.0) * 0.15
            score += rating_normalized
        
        # Click-through rate (0.10 total)
        ctr = self._get_click_through_rate(business.id, db)
        if ctr:
            score += min(ctr / 2.0, 0.10)  # Cap at 0.10 for high CTR
        
        # Recency bonus (0.10 total)
        if business.last_verified:
            days_since_verification = (datetime.utcnow() - business.last_verified).days
            if days_since_verification <= 7:
                score += 0.10
            elif days_since_verification <= 30:
                score += 0.05
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _get_click_through_rate(self, business_id: int, db: Session) -> float:
        """
        Calculate click-through rate for business in last 30 days
        """
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            recommendations = db.query(LeadEvent).filter(
                LeadEvent.business_id == business_id,
                LeadEvent.event_type == "recommendation",
                LeadEvent.created_at >= thirty_days_ago
            ).count()
            
            if recommendations == 0:
                return None
            
            clicks = db.query(LeadEvent).filter(
                LeadEvent.business_id == business_id,
                LeadEvent.clicked == True,
                LeadEvent.created_at >= thirty_days_ago
            ).count()
            
            return (clicks / recommendations) * 100  # Return as percentage
        
        except Exception as e:
            logger.error(f"Error calculating CTR: {str(e)}")
            return None
    
    def recalculate_all(self, db: Session) -> None:
        """
        Recalculate trust scores for all businesses
        """
        try:
            businesses = db.query(Business).all()
            
            for business in businesses:
                new_score = self.calculate_trust_score(business, db)
                business.trust_score = new_score
                business.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"✅ Recalculated trust scores for {len(businesses)} businesses")
        
        except Exception as e:
            logger.error(f"Error recalculating trust scores: {str(e)}")
            db.rollback()
    
    def recalculate_category(self, category: str, db: Session) -> None:
        """
        Recalculate trust scores for businesses in specific category
        """
        try:
            businesses = db.query(Business).filter(
                Business.category == category
            ).all()
            
            for business in businesses:
                new_score = self.calculate_trust_score(business, db)
                business.trust_score = new_score
            
            db.commit()
            logger.info(f"✅ Recalculated trust scores for {len(businesses)} businesses in {category}")
        
        except Exception as e:
            logger.error(f"Error recalculating category scores: {str(e)}")
            db.rollback()
