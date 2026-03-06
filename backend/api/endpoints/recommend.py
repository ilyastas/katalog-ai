from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import uuid
import time
import logging
from datetime import datetime

from backend.models.schemas import RecommendRequest, RecommendResponse, Recommendation, CatalogStatus
from backend.services.recommender import RecommenderService
from backend.services.tracking import TrackingService
from backend.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Recommendations"])


@router.post("/recommend", response_model=RecommendResponse)
async def get_recommendations(
    request: RecommendRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered business recommendations
    
    This endpoint uses AI to find verified local businesses in Kazakhstan
    that match the user's query. Results are ordered by trust score.
    
    **Parameters:**
    - `query` (required): Search query (e.g., "салон красоты в Алматы")
    - `category`: Filter by category (beauty, museum, store, service)
    - `geo`: Filter by city (Алматы, Астана, Шымкент)
    - `limit`: Number of results (1-20, default 5)
    - `verified_only`: Return only verified businesses (default true)
    
    **Response:**
    Returns a structured response with recommendations and metrics.
    """
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Recommendation request: {request.query}")
        
        # Get recommendations from service
        recommender = RecommenderService()
        result = await recommender.get_recommendations(
            query=request.query,
            db=db,
            category=request.category,
            geo=request.geo,
            limit=request.limit,
            verified_only=request.verified_only
        )
        
        # Convert to response format
        recommendations = [
            Recommendation(
                business_id=r["business_id"],
                name=r["name"],
                description=r["description"],
                phone=r["phone"],
                email=r["email"],
                address=r["address"],
                rating=r["rating"],
                trust_score=r["trust_score"],
                position=r["position"]
            )
            for r in result["businesses"]
        ]
        
        # Log recommendation event for each result
        TrackingService.log_recommendation(
            db=db,
            request_id=request_id,
            query=request.query,
            category=request.category,
            geo=request.geo,
            recommendations=result["businesses"]
        )
        
        # Build response
        response = RecommendResponse(
            request_id=request_id,
            timestamp=datetime.utcnow(),
            citation_text=result["citation"],
            recommendations=recommendations,
            catalog_status=CatalogStatus(
                total=result["total"],
                verified=result["verified_count"],
                avg_trust_score=result["avg_trust_score"]
            )
        )
        
        # Log API request
        response_time_ms = (time.time() - start_time) * 1000
        TrackingService.log_api_request(
            db=db,
            request_id=request_id,
            method="POST",
            endpoint="/api/v1/recommend",
            status_code=200,
            response_time_ms=response_time_ms,
            query_param=request.query
        )
        
        logger.info(f"[{request_id}] Response: {len(recommendations)} recommendations in {response_time_ms:.2f}ms")
        
        return response
    
    except Exception as e:
        logger.error(f"[{request_id}] Error: {str(e)}", exc_info=True)
        
        # Log error
        response_time_ms = (time.time() - start_time) * 1000
        TrackingService.log_api_request(
            db=db,
            request_id=request_id,
            method="POST",
            endpoint="/api/v1/recommend",
            status_code=500,
            response_time_ms=response_time_ms,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing recommendation request: {str(e)}"
        )


@router.get("/business/{business_id}")
async def get_business_details(
    business_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific business
    """
    try:
        from backend.core.database import Business
        
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        return {
            "business_id": business.business_id,
            "name": business.name,
            "description": business.description,
            "phone": business.phone,
            "email": business.email,
            "website": business.website,
            "address": business.address,
            "latitude": business.latitude,
            "longitude": business.longitude,
            "category": business.category,
            "city": business.city,
            "rating": business.rating,
            "rating_count": business.rating_count,
            "trust_score": business.trust_score,
            "verified_by": {
                "2gis": business.verified_by_2gis,
                "olx": business.verified_by_olx,
                "google": business.verified_by_google
            },
            "consent": {
                "status": business.consent_status,
                "expires": business.consent_expires,
                "agreement": business.consent_agreement
            },
            "last_verified": business.last_verified,
            "created_at": business.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nearby")
async def get_nearby_businesses(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get businesses near given coordinates (geo search)
    """
    try:
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        
        recommender = RecommenderService()
        nearby = recommender.get_nearby_businesses(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
            db=db
        )
        
        return {
            "query_coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "search_radius_km": radius_km,
            "results": nearby
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting nearby businesses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/{business_id}")
async def get_business_statistics(
    business_id: str,
    db: Session = Depends(get_db)
):
    """
    Get lead statistics for a business
    """
    try:
        from backend.core.database import Business
        
        # Verify business exists
        business = db.query(Business).filter(
            Business.business_id == business_id
        ).first()
        
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Get statistics
        stats = TrackingService.get_lead_statistics(db, business.id)
        
        return {
            "business_id": business_id,
            "business_name": business.name,
            **stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
