"""
Pytest configuration and shared fixtures for all tests
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app
from backend.core.database import Base, get_db

# Test database URL (SQLite for simplicity)
TEST_DATABASE_URL = "sqlite:///./test_katalog.db"


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine (session-scoped)"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    
    # Cleanup test database file
    if os.path.exists("./test_katalog.db"):
        os.remove("./test_katalog.db")


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create fresh test database session for each test"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create FastAPI test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_business(db_session):
    """Create a sample business for testing"""
    from backend.core.database import Business
    
    business = Business(
        business_id="test-beauty-001",
        name="Test Beauty Salon",
        description="Premium beauty services",
        category="beauty",
        city="Алматы",
        phone="+7-700-123-45-67",
        email="test@beauty.kz",
        address="Test Street, Almaty",
        latitude=43.2567,
        longitude=76.9286,
        rating=4.8,
        rating_count=100,
        trust_score=0.85,
        verified_by_2gis=True,
        verified_by_google=True,
        consent_status=True,
        consent_agreement="premium"
    )
    
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)
    
    return business


@pytest.fixture
def multiple_businesses(db_session):
    """Create multiple test businesses"""
    from backend.core.database import Business
    
    businesses = [
        Business(
            business_id=f"test-{category}-001",
            name=f"Test {category.title()} Business",
            category=category,
            city="Алматы",
            phone=f"+7-70{idx}-000-00-00",
            email=f"test-{idx}@test.kz",
            trust_score=0.7 + (idx * 0.05),
            verified_by_2gis=(idx % 2 == 0),
            verified_by_google=True,
            consent_status=True
        )
        for idx, category in enumerate(["beauty", "store", "service", "museum"], 1)
    ]
    
    for business in businesses:
        db_session.add(business)
    
    db_session.commit()
    
    return businesses


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set test environment variables"""
    test_env = {
        "ENVIRONMENT": "test",
        "DATABASE_URL": TEST_DATABASE_URL,
        "OPENAI_API_KEY": "test-openai-key",
        "GOOGLE_AI_API_KEY": "test-google-key",
        "TWOGIS_API_KEY": "test-2gis-key",
        "GOOGLE_PLACES_KEY": "test-places-key",
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env
