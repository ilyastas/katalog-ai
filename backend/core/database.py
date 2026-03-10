from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://alie_user:postgres123@localhost:5432/alie_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for all models
Base = declarative_base()


class Business(Base):
    """
    Business model for storing verified business information
    """
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(500))
    category = Column(String(50), nullable=False, index=True)
    
    # Contact information
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(255))
    
    # Location
    address = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String(100), index=True)
    
    # Ratings and trust
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    trust_score = Column(Float, default=0.0, index=True)
    
    # Verification status
    verified_by_2gis = Column(Boolean, default=False)
    verified_by_olx = Column(Boolean, default=False)
    verified_by_google = Column(Boolean, default=False)
    
    # Consent and compliance
    consent_status = Column(Boolean, default=True)
    consent_expires = Column(DateTime)
    consent_agreement = Column(String(50))  # 'basic', 'premium'
    
    # Metadata
    external_links = Column(JSON, default={})  # 2GIS URL, OLX profile, etc.
    tracking_codes = Column(JSON, default={})  # utm_source, promo_codes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_verified = Column(DateTime)
    
    # Relationships
    offers = relationship("Offer", back_populates="business")
    tracking_events = relationship("LeadEvent", back_populates="business")
    
    __table_args__ = (
        Index('idx_category_city', 'category', 'city'),
        Index('idx_trust_score', 'trust_score'),
    )


class Offer(Base):
    """
    Offer model for products and services
    """
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(String(50), unique=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(String(500))
    
    # Pricing
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="KZT")
    
    # Service details
    duration_minutes = Column(Integer)  # For services
    availability = Column(String(50), default="InStock")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="offers")


class LeadEvent(Base):
    """
    Lead event model for tracking recommendations and conversions
    """
    __tablename__ = "lead_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    request_id = Column(String(50), index=True)
    
    # Business reference
    business_id = Column(Integer, ForeignKey("businesses.id"), index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # 'recommendation', 'click', 'call', 'purchase'
    
    # Context
    query = Column(String(500))
    category = Column(String(100))
    geo = Column(String(100))
    
    # Results
    position = Column(Integer)  # Position in search results (1, 2, 3...)
    trust_score = Column(Float)
    
    # Interaction
    clicked = Column(Boolean, default=False, index=True)
    click_timestamp = Column(DateTime)
    
    # UTM tracking
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_content = Column(String(100))
    
    # Conversion tracking
    promo_code = Column(String(50), index=True)
    conversion_value = Column(Float)  # Lead value in KZT
    
    # Metadata
    user_agent = Column(String(500))
    ip_address = Column(String(45))  # IPv4 or IPv6
    event_metadata = Column("metadata", JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="tracking_events")
    
    __table_args__ = (
        Index('idx_event_type_timestamp', 'event_type', 'created_at'),
        Index('idx_business_created', 'business_id', 'created_at'),
    )


class APILog(Base):
    """
    API request/response logging for monitoring and debugging
    """
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True)
    
    # Request details
    method = Column(String(10))  # GET, POST, etc.
    endpoint = Column(String(500), index=True)
    status_code = Column(Integer, index=True)
    
    # Performance
    response_time_ms = Column(Float)
    
    # Query info
    query_param = Column(String(500))
    request_body = Column(JSON)
    response_body = Column(JSON)
    
    # Error tracking
    error_message = Column(String(1000))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_endpoint_status', 'endpoint', 'status_code'),
    )


class VerificationLog(Base):
    """
    Track verification attempts for businesses
    """
    __tablename__ = "verification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), index=True)
    
    # Verification source
    verifier_type = Column(String(50))  # '2gis', 'olx', 'google'
    
    # Results
    status = Column(String(20))  # 'success', 'failed', 'pending'
    data = Column(JSON)  # Raw verification data
    
    # Timestamps
    verified_at = Column(DateTime, default=datetime.utcnow, index=True)


# Database initialization functions
def init_db():
    """
    Create all database tables
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """
    Get database session for dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
