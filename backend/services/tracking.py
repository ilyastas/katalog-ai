from sqlalchemy.orm import Session
from backend.core.database import LeadEvent, APILog
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class TrackingService:
    """
    Service for tracking lead events and API usage
    """
    
    @staticmethod
    def log_recommendation(
        db: Session,
        request_id: str,
        query: str,
        category: str = None,
        geo: str = None,
        recommendations: list = None,
        utm_source: str = "ai_assistant",
        utm_campaign: str = None
    ) -> None:
        """
        Log a recommendation event for each business in results
        """
        try:
            if not recommendations:
                recommendations = []
            
            for idx, business in enumerate(recommendations, 1):
                event = LeadEvent(
                    event_id=str(uuid.uuid4()),
                    request_id=request_id,
                    business_id=business.get("business_id"),
                    event_type="recommendation",
                    query=query,
                    category=category,
                    geo=geo,
                    position=idx,
                    trust_score=business.get("trust_score", 0.0),
                    utm_source=utm_source,
                    utm_campaign=utm_campaign or "search",
                    promo_code=business.get("promo_code")
                )
                db.add(event)
            
            db.commit()
            logger.info(f"Logged {len(recommendations)} recommendation events")
        
        except Exception as e:
            logger.error(f"Error logging recommendations: {str(e)}")
            db.rollback()
    
    @staticmethod
    def log_click(
        db: Session,
        event_id: str,
        business_id: str,
        promo_code: str = None
    ) -> None:
        """
        Log a click event when user interacts with recommendation
        """
        try:
            event = db.query(LeadEvent).filter(
                LeadEvent.business_id == business_id,
                LeadEvent.created_at >= datetime.utcnow()
            ).first()
            
            if not event:
                # Create new click event
                event = LeadEvent(
                    event_id=str(uuid.uuid4()),
                    business_id=business_id,
                    event_type="click",
                    clicked=True,
                    click_timestamp=datetime.utcnow(),
                    promo_code=promo_code
                )
                db.add(event)
            else:
                # Update existing event
                event.clicked = True
                event.click_timestamp = datetime.utcnow()
            
            db.commit()
            logger.info(f"Logged click event for business {business_id}")
        
        except Exception as e:
            logger.error(f"Error logging click: {str(e)}")
            db.rollback()
    
    @staticmethod
    def log_api_request(
        db: Session,
        request_id: str,
        method: str,
        endpoint: str,
        status_code: int,
        response_time_ms: float,
        query_param: str = None,
        error_message: str = None
    ) -> None:
        """
        Log API request for monitoring and debugging
        """
        try:
            log = APILog(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time_ms=response_time_ms,
                query_param=query_param,
                error_message=error_message
            )
            db.add(log)
            db.commit()
        
        except Exception as e:
            logger.error(f"Error logging API request: {str(e)}")
            db.rollback()
    
    @staticmethod
    def get_lead_statistics(db: Session, business_id: str = None) -> dict:
        """
        Get lead statistics for dashboard
        """
        try:
            query = db.query(LeadEvent)
            
            if business_id:
                query = query.filter(LeadEvent.business_id == business_id)
            
            total_events = query.count()
            
            clicks = query.filter(LeadEvent.clicked == True).count()
            
            click_through_rate = (clicks / total_events * 100) if total_events > 0 else 0
            
            recommendations = query.filter(
                LeadEvent.event_type == "recommendation"
            ).count()
            
            return {
                "total_events": total_events,
                "recommendations": recommendations,
                "clicks": clicks,
                "click_through_rate": round(click_through_rate, 2),
                "conversion_rate": 0  # To be calculated with actual conversions
            }
        
        except Exception as e:
            logger.error(f"Error getting lead statistics: {str(e)}")
            return {}
    
    @staticmethod
    def calculate_lead_value(db: Session, promo_code: str = None) -> float:
        """
        Calculate total lead value for billing purposes
        """
        try:
            query = db.query(LeadEvent).filter(
                LeadEvent.event_type == "recommendation"
            )
            
            if promo_code:
                query = query.filter(LeadEvent.promo_code == promo_code)
            
            # Default lead value: 1000 KZT per recommendation + bonus for clicks
            base_value = 1000  # KZT per recommendation
            click_bonus = 500   # KZT per click
            
            recommendations = query.count()
            clicks = query.filter(LeadEvent.clicked == True).count()
            
            total_value = (recommendations * base_value) + (clicks * click_bonus)
            
            return total_value
        
        except Exception as e:
            logger.error(f"Error calculating lead value: {str(e)}")
            return 0.0
