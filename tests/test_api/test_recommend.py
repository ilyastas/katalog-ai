"""
Unit tests for recommendation API endpoint
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from backend.main import app
from backend.core.database import Base, get_db, Business, SessionLocal


# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    
    # Add test data
    test_businesses = [
        Business(
            business_id="test-beauty-001",
            name="Test Beauty Salon",
            description="Premium beauty salon",
            category="beauty",
            phone="+7-700-123-45-67",
            email="test@beauty.kz",
            address="Test St, Almaty",
            latitude=43.2567,
            longitude=76.9286,
            city="Алматы",
            rating=4.8,
            rating_count=100,
            trust_score=0.95,
            verified_by_2gis=True,
            verified_by_olx=True,
            verified_by_google=True,
            consent_status=True,
            consent_agreement="premium"
        ),
        Business(
            business_id="test-store-001",
            name="Test Tech Store",
            description="Electronics store",
            category="store",
            phone="+7-701-234-56-78",
            email="test@store.kz",
            address="Market St, Almaty",
            latitude=43.2380,
            longitude=76.9450,
            city="Алматы",
            rating=4.5,
            rating_count=50,
            trust_score=0.85,
            verified_by_2gis=True,
            verified_by_google=True,
            consent_status=True,
            consent_agreement="basic"
        )
    ]
    
    for business in test_businesses:
        db.add(business)
    
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """Create test client"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# Tests
class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # 200 if all services healthy, 503 if degraded
        assert "status" in response.json()
        assert "version" in response.json()


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "ALIE - AI Lead Intelligence Engine"
        assert "version" in data
        assert "endpoints" in data


class TestRecommendEndpoint:
    """Test /recommend endpoint"""
    
    def test_recommend_simple_query(self, client):
        """Test recommendation with simple query"""
        response = client.post(
            "/api/v1/recommend/recommend",
            json={
                "query": "beauty salon"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "request_id" in data
        assert "timestamp" in data
        assert "citation_text" in data
        assert "recommendations" in data
        assert "catalog_status" in data
        
        # Verify recommendations structure
        if data["recommendations"]:
            rec = data["recommendations"][0]
            assert "business_id" in rec
            assert "name" in rec
            assert "trust_score" in rec
            assert "position" in rec
    
    def test_recommend_with_category_filter(self, client):
        """Test recommendation with category filter"""
        response = client.post(
            "/api/v1/recommend/recommend",
            json={
                "query": "salon",
                "category": "beauty"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return beauty businesses
        for rec in data["recommendations"]:
            assert rec.get("category") == "beauty" or rec.get("category") is None
    
    def test_recommend_with_limit(self, client):
        """Test recommendation with limit parameter"""
        response = client.post(
            "/api/v1/recommend/recommend",
            json={
                "query": "test",
                "limit": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should respect limit
        assert len(data["recommendations"]) <= 1
    
    def test_recommend_empty_query(self, client):
        """Test recommendation with empty query"""
        response = client.post(
            "/api/v1/recommend/recommend",
            json={
                "query": ""
            }
        )
        
        # Should fail validation
        assert response.status_code == 422
    
    def test_recommend_verified_only(self, client):
        """Test recommendation with verified_only filter"""
        response = client.post(
            "/api/v1/recommend/recommend",
            json={
                "query": "test",
                "verified_only": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # All results should be verified
        for rec in data["recommendations"]:
            assert rec.get("verified") is True or rec.get("verified") is None


class TestBusinessDetailsEndpoint:
    """Test /business/{business_id} endpoint"""
    
    def test_get_existing_business(self, client):
        """Test getting existing business"""
        response = client.get("/api/v1/recommend/business/test-beauty-001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["business_id"] == "test-beauty-001"
        assert data["name"] == "Test Beauty Salon"
        assert "verified_by" in data
        assert "consent" in data
    
    def test_get_nonexistent_business(self, client):
        """Test getting non-existent business"""
        response = client.get("/api/v1/recommend/business/nonexistent-id")
        
        assert response.status_code == 404


class TestNearbyEndpoint:
    """Test /nearby endpoint"""
    
    def test_nearby_search(self, client):
        """Test nearby search"""
        response = client.get(
            "/api/v1/recommend/nearby",
            params={
                "latitude": 43.2567,
                "longitude": 76.9286,
                "radius_km": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "query_coordinates" in data
        assert "search_radius_km" in data
    
    def test_nearby_invalid_coordinates(self, client):
        """Test nearby search with invalid coordinates"""
        response = client.get(
            "/api/v1/recommend/nearby",
            params={
                "latitude": 95.0,  # Invalid: > 90
                "longitude": 76.9286
            }
        )
        
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
