"""
Analytics Tasks - Celery tasks for analytics calculations and reporting
"""

import logging
from typing import Dict
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.workers.celery_app import app
from backend.core.database import SessionLocal, Business, LeadEvent, APILog
from backend.services.tracking import TrackingService

logger = logging.getLogger(__name__)


@app.task(bind=True)
def calculate_daily_statistics(self) -> Dict:
    """
    Calculate daily statistics for all businesses
    Aggregates clicks, impressions, and lead values
    
    Returns:
        Daily statistics summary
    """
    db = SessionLocal()
    
    try:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        today = yesterday + timedelta(days=1)
        
        events = db.query(LeadEvent).filter(
            LeadEvent.created_at >= datetime.combine(yesterday, datetime.min.time()),
            LeadEvent.created_at < datetime.combine(today, datetime.min.time())
        ).all()
        
        results = {
            "date": yesterday.isoformat(),
            "total_events": len(events),
            "recommendations": 0,
            "clicks": 0,
            "total_value": 0,
            "by_category": {},
            "by_business": {}
        }
        
        tracking_service = TrackingService()
        
        for event in events:
            if event.event_type == "recommendation":
                results["recommendations"] += 1
            elif event.event_type == "click":
                results["clicks"] += 1
            
            value = tracking_service.calculate_lead_value(event)
            results["total_value"] += value
            
            business = event.business
            if business:
                cat = business.category
                if cat not in results["by_category"]:
                    results["by_category"][cat] = {
                        "events": 0,
                        "value": 0,
                        "businesses": {}
                    }
                
                results["by_category"][cat]["events"] += 1
                results["by_category"][cat]["value"] += value
                
                bid = business.business_id
                if bid not in results["by_business"]:
                    results["by_business"][bid] = {
                        "name": business.name,
                        "events": 0,
                        "value": 0
                    }
                
                results["by_business"][bid]["events"] += 1
                results["by_business"][bid]["value"] += value
        
        logger.info(f"Daily stats: {len(events)} events, {results['total_value']} KZT")
        
        return results
    
    except Exception as exc:
        logger.error(f"Error in daily statistics: {str(exc)}", exc_info=True)
        return {"status": "failed", "error": str(exc)}
    
    finally:
        db.close()


@app.task(bind=True)
def calculate_monthly_report(self) -> Dict:
    """
    Generate monthly report with key metrics
    
    Returns:
        Monthly analytics report
    """
    db = SessionLocal()
    
    try:
        today = datetime.utcnow().date()
        month_ago = today - timedelta(days=30)
        
        events = db.query(LeadEvent).filter(
            LeadEvent.created_at >= datetime.combine(month_ago, datetime.min.time()),
            LeadEvent.created_at <= datetime.combine(today, datetime.max.time())
        ).all()
        
        businesses = db.query(Business).all()
        
        total_recommendations = len([e for e in events if e.event_type == "recommendation"])
        total_clicks = len([e for e in events if e.event_type == "click"])
        ctr = (total_clicks / total_recommendations * 100) if total_recommendations > 0 else 0
        
        response_times = db.query(APILog).filter(
            APILog.created_at >= datetime.combine(month_ago, datetime.min.time()),
            APILog.created_at <= datetime.combine(today, datetime.max.time())
        ).all()
        
        avg_response_time = 0
        if response_times:
            total_time = sum(log.response_time for log in response_times if log.response_time)
            avg_response_time = total_time / len(response_times) if response_times else 0
        
        verified_count = len([b for b in businesses if b.trust_score > 0.5])
        
        results = {
            "period": f"{month_ago.isoformat()} to {today.isoformat()}",
            "metrics": {
                "total_businesses": len(businesses),
                "verified_businesses": verified_count,
                "verification_rate": round((verified_count / len(businesses) * 100) if businesses else 0, 2),
                "total_recommendations": total_recommendations,
                "total_clicks": total_clicks,
                "click_through_rate": round(ctr, 2),
                "average_response_time_ms": round(avg_response_time, 2),
                "total_api_calls": len(response_times)
            }
        }
        
        logger.info(f"Monthly report generated - CTR: {ctr:.2f}%")
        
        return results
    
    except Exception as exc:
        logger.error(f"Error generating monthly report: {str(exc)}", exc_info=True)
        return {"status": "failed", "error": str(exc)}
    
    finally:
        db.close()


@app.task(bind=True)
def cleanup_old_logs(self, days_to_keep: int = 90) -> Dict:
    """
    Clean up old logs and archived data
    
    Args:
        days_to_keep: Number of days to retain
    
    Returns:
        Cleanup summary
    """
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        old_api_logs = db.query(APILog).filter(
            APILog.created_at < cutoff_date
        ).delete()
        
        logger.info(f"Deleted {old_api_logs} old API logs")
        
        db.commit()
        
        results = {
            "status": "success",
            "cleanup_date": cutoff_date.isoformat(),
            "deleted": {
                "api_logs": old_api_logs
            }
        }
        
        return results
    
    except Exception as exc:
        logger.error(f"Error cleaning up logs: {str(exc)}")
        db.rollback()
        return {"status": "failed", "error": str(exc)}
    
    finally:
        db.close()
