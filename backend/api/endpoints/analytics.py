"""
Analytics Endpoints - Query aggregated statistics and reports
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import SessionLocal, LeadEvent, Business, APILog

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    responses={404: {"description": "Not found"}}
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/daily")
async def get_daily_statistics(
    date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get daily statistics for a specific date
    
    Query Parameters:
    - date: ISO format date (YYYY-MM-DD). Defaults to yesterday
    
    Response includes:
    - Event counts (recommendations, clicks, calls)
    - Revenue metrics
    - Category breakdown
    - Business performance
    
    Example: GET /api/v1/analytics/daily?date=2024-01-19
    
    Response:
    ```json
    {
        "date": "2024-01-19",
        "total_events": 1245,
        "recommendations": 450,
        "clicks": 380,
        "calls": 415,
        "total_lead_value_kzt": 125000,
        "average_value_per_lead": 100.40,
        "click_through_rate": 84.4,
        "by_category": {
            "hair_salon": {
                "events": 245,
                "recommendations": 100,
                "clicks": 95,
                "calls": 50,
                "value": 25000
            }
        }
    }
    ```
    """
    
    try:
        # Parse date
        if date:
            target_date = datetime.fromisoformat(date).date()
        else:
            target_date = (datetime.utcnow() - timedelta(days=1)).date()
        
        # Calculate date range
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        
        # Query events for the date
        events = db.query(LeadEvent).filter(
            LeadEvent.created_at >= start_time,
            LeadEvent.created_at <= end_time
        ).all()
        
        if not events:
            return {
                "date": target_date.isoformat(),
                "total_events": 0,
                "recommendations": 0,
                "clicks": 0,
                "calls": 0,
                "total_lead_value_kzt": 0,
                "average_value_per_lead": 0,
                "click_through_rate": 0,
                "by_category": {},
                "message": "No events for this date"
            }
        
        # Aggregate statistics
        recommendations = sum(1 for e in events if e.event_type == "recommendation")
        clicks = sum(1 for e in events if e.event_type == "click")
        calls = sum(1 for e in events if e.event_type == "call")
        
        # Calculate values
        total_value = sum(e.lead_value or 0 for e in events if e.event_type == "click")
        average_value = total_value / clicks if clicks > 0 else 0
        ctr = (clicks / recommendations * 100) if recommendations > 0 else 0
        
        # Group by category
        by_category = {}
        for event in events:
            category = event.business.category if event.business else "unknown"
            
            if category not in by_category:
                by_category[category] = {
                    "events": 0,
                    "recommendations": 0,
                    "clicks": 0,
                    "calls": 0,
                    "value": 0
                }
            
            by_category[category]["events"] += 1
            by_category[category]["value"] += event.lead_value or 0
            
            if event.event_type == "recommendation":
                by_category[category]["recommendations"] += 1
            elif event.event_type == "click":
                by_category[category]["clicks"] += 1
            elif event.event_type == "call":
                by_category[category]["calls"] += 1
        
        logger.info(f"Daily statistics retrieved for {target_date}: {len(events)} events")
        
        return {
            "date": target_date.isoformat(),
            "total_events": len(events),
            "recommendations": recommendations,
            "clicks": clicks,
            "calls": calls,
            "total_lead_value_kzt": round(total_value, 2),
            "average_value_per_lead": round(average_value, 2),
            "click_through_rate": round(ctr, 2),
            "by_category": by_category
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")
    except Exception as e:
        logger.error(f"Error calculating daily statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/monthly")
async def get_monthly_report(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get monthly report (rolling 30-day period)
    
    Query Parameters:
    - days: Number of days to include (default 30)
    
    Returns key metrics for performance dashboard:
    - Total events and breakdown by type
    - Lead value and revenue
    - Click-through rate
    - Verification status
    - Average API response time
    - Top performing categories and businesses
    
    Response:
    ```json
    {
        "period_start": "2023-12-21",
        "period_end": "2024-01-19",
        "days": 30,
        "total_events": 35250,
        "total_lead_value_kzt": 3500000,
        "average_daily_value": 116666.67,
        "click_through_rate": 82.3,
        "businesses_verified": 185,
        "total_businesses": 250,
        "verification_rate": 74.0,
        "api_response_time_ms": 245,
        "top_categories": [
            {
                "category": "hair_salon",
                "events": 8900,
                "value": 890000,
                "ctr": 84.5
            }
        ],
        "top_businesses": [
            {
                "business_id": 1,
                "name": "Salon A",
                "events": 450,
                "clicks": 380,
                "value": 38000,
                "trust_score": 0.92
            }
        ]
    }
    ```
    """
    
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=400,
                detail="Days must be between 1 and 365"
            )
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query events
        events = db.query(LeadEvent).filter(
            LeadEvent.created_at >= start_date,
            LeadEvent.created_at <= end_date
        ).all()
        
        # Aggregate
        recommendations = sum(1 for e in events if e.event_type == "recommendation")
        clicks = sum(1 for e in events if e.event_type == "click")
        calls = sum(1 for e in events if e.event_type == "call")
        
        total_value = sum(e.lead_value or 0 for e in events if e.event_type == "click")
        avg_daily_value = total_value / days if days > 0 else 0
        ctr = (clicks / recommendations * 100) if recommendations > 0 else 0
        
        # Verification stats
        verified_count = db.query(Business).filter(
            Business.trust_score > 0.5
        ).count()
        total_count = db.query(Business).count()
        verification_rate = (verified_count / total_count * 100) if total_count > 0 else 0
        
        # API performance
        api_logs = db.query(APILog).filter(
            APILog.created_at >= start_date
        ).all()
        
        avg_response_time = 0
        if api_logs:
            response_times = [log.response_time_ms for log in api_logs if log.response_time_ms]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Top categories
        by_category = {}
        for event in events:
            category = event.business.category if event.business else "unknown"
            
            if category not in by_category:
                by_category[category] = {
                    "events": 0,
                    "value": 0,
                    "clicks": 0,
                    "recommendations": 0
                }
            
            by_category[category]["events"] += 1
            by_category[category]["value"] += event.lead_value or 0
            
            if event.event_type == "click":
                by_category[category]["clicks"] += 1
            elif event.event_type == "recommendation":
                by_category[category]["recommendations"] += 1
        
        # Calculate CTR by category
        for cat in by_category.values():
            cat["ctr"] = (cat["clicks"] / cat["recommendations"] * 100) if cat["recommendations"] > 0 else 0
        
        # Sort top categories by events
        top_categories = sorted(
            by_category.items(),
            key=lambda x: x[1]["events"],
            reverse=True
        )[:5]
        
        # Top businesses (by events in period)
        business_stats = {}
        for event in events:
            if event.business_id:
                if event.business_id not in business_stats:
                    business_stats[event.business_id] = {
                        "name": event.business.name if event.business else "Unknown",
                        "events": 0,
                        "clicks": 0,
                        "value": 0,
                        "trust_score": event.business.trust_score if event.business else 0
                    }
                
                business_stats[event.business_id]["events"] += 1
                business_stats[event.business_id]["value"] += event.lead_value or 0
                
                if event.event_type == "click":
                    business_stats[event.business_id]["clicks"] += 1
        
        # Sort top businesses
        top_businesses = sorted(
            [
                {"business_id": k, **v}
                for k, v in business_stats.items()
            ],
            key=lambda x: x["events"],
            reverse=True
        )[:10]
        
        logger.info(f"Monthly report generated for {days} days: {len(events)} events")
        
        return {
            "period_start": start_date.date().isoformat(),
            "period_end": end_date.date().isoformat(),
            "days": days,
            "total_events": len(events),
            "recommendations": recommendations,
            "clicks": clicks,
            "calls": calls,
            "total_lead_value_kzt": round(total_value, 2),
            "average_daily_value": round(avg_daily_value, 2),
            "click_through_rate": round(ctr, 2),
            "businesses_verified": verified_count,
            "total_businesses": total_count,
            "verification_rate": round(verification_rate, 2),
            "api_response_time_ms": round(avg_response_time, 2),
            "top_categories": [
                {
                    "category": cat[0],
                    **cat[1]
                }
                for cat in top_categories
            ],
            "top_businesses": top_businesses
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating monthly report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/category/{category}")
async def get_category_analytics(
    category: str,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get analytics for a specific category
    
    Path Parameters:
    - category: Category name
    
    Query Parameters:
    - days: Number of days to include (default 30)
    
    Response includes category-specific metrics and top businesses
    """
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query events for category
        events = db.query(LeadEvent).join(Business).filter(
            Business.category == category,
            LeadEvent.created_at >= start_date,
            LeadEvent.created_at <= end_date
        ).all()
        
        if not events:
            raise HTTPException(
                status_code=404,
                detail=f"No events found for category '{category}'"
            )
        
        # Aggregate
        recommendations = sum(1 for e in events if e.event_type == "recommendation")
        clicks = sum(1 for e in events if e.event_type == "click")
        calls = sum(1 for e in events if e.event_type == "call")
        
        total_value = sum(e.lead_value or 0 for e in events if e.event_type == "click")
        ctr = (clicks / recommendations * 100) if recommendations > 0 else 0
        
        # Business breakdown
        business_stats = {}
        for event in events:
            if event.business_id:
                if event.business_id not in business_stats:
                    business_stats[event.business_id] = {
                        "name": event.business.name,
                        "events": 0,
                        "clicks": 0,
                        "value": 0,
                        "trust_score": event.business.trust_score
                    }
                
                business_stats[event.business_id]["events"] += 1
                business_stats[event.business_id]["value"] += event.lead_value or 0
                
                if event.event_type == "click":
                    business_stats[event.business_id]["clicks"] += 1
        
        # Top businesses
        top_businesses = sorted(
            [
                {"business_id": k, **v}
                for k, v in business_stats.items()
            ],
            key=lambda x: x["events"],
            reverse=True
        )[:10]
        
        logger.info(f"Category analytics retrieved for '{category}': {len(events)} events")
        
        return {
            "category": category,
            "period_start": start_date.date().isoformat(),
            "period_end": end_date.date().isoformat(),
            "days": days,
            "total_events": len(events),
            "recommendations": recommendations,
            "clicks": clicks,
            "calls": calls,
            "total_lead_value_kzt": round(total_value, 2),
            "click_through_rate": round(ctr, 2),
            "top_businesses": top_businesses
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/business/{business_id}")
async def get_business_analytics(
    business_id: int,
    days: int = 90,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get detailed analytics for a specific business
    
    Path Parameters:
    - business_id: Business ID
    
    Query Parameters:
    - days: Number of days to analyze (default 90)
    
    Response includes performance metrics and trends
    """
    
    try:
        # Get business
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business {business_id} not found"
            )
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query events
        events = db.query(LeadEvent).filter(
            LeadEvent.business_id == business_id,
            LeadEvent.created_at >= start_date,
            LeadEvent.created_at <= end_date
        ).all()
        
        if not events:
            return {
                "business_id": business_id,
                "business_name": business.name,
                "category": business.category,
                "total_events": 0,
                "message": "No events for this business in period"
            }
        
        # Aggregate
        recommendations = sum(1 for e in events if e.event_type == "recommendation")
        clicks = sum(1 for e in events if e.event_type == "click")
        calls = sum(1 for e in events if e.event_type == "call")
        
        total_value = sum(e.lead_value or 0 for e in events if e.event_type == "click")
        ctr = (clicks / recommendations * 100) if recommendations > 0 else 0
        avg_value = total_value / clicks if clicks > 0 else 0
        
        # Daily breakdown
        daily_stats = {}
        for event in events:
            date_key = event.created_at.date().isoformat()
            
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    "events": 0,
                    "clicks": 0,
                    "value": 0
                }
            
            daily_stats[date_key]["events"] += 1
            daily_stats[date_key]["value"] += event.lead_value or 0
            
            if event.event_type == "click":
                daily_stats[date_key]["clicks"] += 1
        
        logger.info(f"Business analytics retrieved for {business_id}: {len(events)} events")
        
        return {
            "business_id": business_id,
            "business_name": business.name,
            "category": business.category,
            "trust_score": business.trust_score,
            "period_start": start_date.date().isoformat(),
            "period_end": end_date.date().isoformat(),
            "days": days,
            "total_events": len(events),
            "recommendations": recommendations,
            "clicks": clicks,
            "calls": calls,
            "total_lead_value_kzt": round(total_value, 2),
            "average_value_per_click": round(avg_value, 2),
            "click_through_rate": round(ctr, 2),
            "daily_breakdown": daily_stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
