from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CategoryEnum(str, Enum):
    """Allowed business categories"""
    BEAUTY = "beauty"
    MUSEUM = "museum"
    STORE = "store"
    SERVICE = "service"
    RESTAURANT = "restaurant"
    HOTEL = "hotel"


class BusinessBase(BaseModel):
    """Base Business model"""
    business_id: str = Field(..., description="Unique business identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Business name")
    description: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, description="Contact phone")
    email: Optional[EmailStr] = None
    category: CategoryEnum
    address: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    rating: Optional[float] = Field(None, ge=0, le=5)
    trust_score: Optional[float] = Field(0.0, ge=0, le=1)
    
    class Config:
        use_enum_values = True


class Business(BusinessBase):
    """Complete Business model with metadata"""
    verified_by_2gis: bool = False
    verified_by_olx: bool = False
    verified_by_google: bool = False
    consent_status: bool = True
    consent_expires: Optional[datetime] = None
    last_verified: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "beauty-001",
                "name": "Бьюти-салон Premium",
                "description": "Премиум-салон красоты",
                "phone": "+7-700-123-45-67",
                "email": "info@beautypremium.kz",
                "category": "beauty",
                "address": "ул. Жибек Жолы, 50, Алматы",
                "latitude": 43.2567,
                "longitude": 76.9286,
                "rating": 4.8,
                "trust_score": 0.95,
                "verified_by_2gis": True,
                "verified_by_olx": True,
                "verified_by_google": True,
                "consent_status": True,
                "consent_expires": "2027-03-01T00:00:00"
            }
        }


class RecommendRequest(BaseModel):
    """Request model for /recommend endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    category: Optional[CategoryEnum] = Field(None, description="Filter by business category")
    geo: Optional[str] = Field(None, description="City name (Алматы, Астана, Шымкент)")
    limit: int = Field(5, ge=1, le=20, description="Number of recommendations (1-20)")
    verified_only: bool = Field(True, description="Only verified businesses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "салон красоты в Алматы",
                "category": "beauty",
                "geo": "Алматы",
                "limit": 5,
                "verified_only": True
            }
        }


class Recommendation(BaseModel):
    """Single recommendation"""
    business_id: str
    name: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    trust_score: float
    distance_km: Optional[float] = None
    position: int = Field(..., description="Position in search results")


class CatalogStatus(BaseModel):
    """Catalog statistics"""
    total: int
    verified: int
    avg_trust_score: float


class RecommendResponse(BaseModel):
    """Response model for /recommend endpoint"""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citation_text: str = Field(..., description="Citation for AI assistant")
    recommendations: List[Recommendation] = Field(...)
    catalog_status: CatalogStatus = Field(...)
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req-12345",
                "timestamp": "2026-03-05T12:00:00",
                "citation_text": "По запросу 'салон красоты в Алматы' найдено 3 проверенных бизнеса",
                "recommendations": [
                    {
                        "business_id": "beauty-001",
                        "name": "Бьюти-салон Premium",
                        "description": "Премиум-салон красоты",
                        "phone": "+7-700-123-45-67",
                        "email": "info@beautypremium.kz",
                        "address": "ул. Жибек Жолы, 50",
                        "rating": 4.8,
                        "trust_score": 0.95,
                        "distance_km": 2.1,
                        "position": 1
                    }
                ],
                "catalog_status": {
                    "total": 10,
                    "verified": 10,
                    "avg_trust_score": 0.91
                }
            }
        }


class OfferBase(BaseModel):
    """Base Offer model"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    currency: str = Field("KZT", min_length=3, max_length=3)
    duration_minutes: Optional[int] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    services: Dict[str, bool] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
