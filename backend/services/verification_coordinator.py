"""
Verification Coordinator - Orchestrates verification across multiple APIs
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.database import Business, VerificationLog
from backend.verifiers.two_gis import TwoGISVerifier
from backend.verifiers.olx_verifier import OLXVerifier
from backend.verifiers.google_verifier import GooglePlacesVerifier
from backend.services.trust_scorer import TrustScorer

logger = logging.getLogger(__name__)


class VerificationCoordinator:
    """
    Coordinates verification across multiple APIs
    Manages verification attempts and status tracking
    """
    
    def __init__(
        self,
        two_gis_key: str,
        apify_token: str,
        google_key: str
    ):
        """
        Initialize with API credentials
        
        Args:
            two_gis_key: 2ГИС API key
            apify_token: Apify token for OLX
            google_key: Google Places API key
        """
        self.two_gis = TwoGISVerifier(two_gis_key) if two_gis_key else None
        self.olx = OLXVerifier(apify_token) if apify_token else None
        self.google = GooglePlacesVerifier(google_key) if google_key else None
        self.trust_scorer = TrustScorer()
    
    async def verify_business(
        self,
        business: Business,
        db: Session
    ) -> Dict:
        """
        Verify business across all available APIs
        
        Args:
            business: Business model instance
            db: Database session
        
        Returns:
            Dictionary with verification results
        """
        results = {
            "business_id": business.business_id,
            "name": business.name,
            "verifications": {},
            "external_links": business.external_links or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 2ГИС Verification
        if self.two_gis:
            try:
                two_gis_result = await self.two_gis.verify_business(
                    business.name,
                    address=business.address,
                    city=business.city
                )
                
                results["verifications"]["2gis"] = {
                    "verified": two_gis_result.get("verified", False),
                    "status": two_gis_result.get("status"),
                    "2gis_id": two_gis_result.get("2gis_id"),
                    "2gis_url": two_gis_result.get("2gis_url")
                }
                
                # Update business record
                if two_gis_result.get("verified"):
                    business.verified_2gis = True
                    if two_gis_result.get("2gis_url"):
                        results["external_links"]["2gis_url"] = two_gis_result["2gis_url"]
                    if two_gis_result.get("2gis_id"):
                        results["external_links"]["2gis_id"] = two_gis_result["2gis_id"]
                
                # Log verification attempt
                await self._log_verification(
                    db, business.business_id, "2gis", True if two_gis_result.get("verified") else False, two_gis_result
                )
            
            except Exception as e:
                logger.warning(f"2GIS verification failed for {business.name}: {str(e)}")
                results["verifications"]["2gis"] = {"error": str(e)}
        
        # Google Places Verification
        if self.google:
            try:
                google_result = await self.google.search_business(
                    business.name,
                    address=business.address
                )
                
                results["verifications"]["google"] = {
                    "verified": google_result.get("verified", False),
                    "status": google_result.get("status"),
                    "google_url": google_result.get("google_url"),
                    "rating": google_result.get("rating"),
                    "review_count": google_result.get("review_count")
                }
                
                # Update business record
                if google_result.get("verified"):
                    business.verified_google = True
                    if google_result.get("rating"):
                        business.google_rating = google_result["rating"]
                    if google_result.get("review_count"):
                        business.google_reviews_count = google_result["review_count"]
                    if google_result.get("google_url"):
                        results["external_links"]["google_url"] = google_result["google_url"]
                
                # Log verification attempt
                await self._log_verification(
                    db, business.business_id, "google", True if google_result.get("verified") else False, google_result
                )
            
            except Exception as e:
                logger.warning(f"Google verification failed for {business.name}: {str(e)}")
                results["verifications"]["google"] = {"error": str(e)}
        
        # OLX Verification (if OLX profile exists)
        if self.olx and business.external_links and "olx_url" in business.external_links:
            try:
                olx_result = await self.olx.verify_seller(
                    business.external_links["olx_url"]
                )
                
                results["verifications"]["olx"] = {
                    "verified": olx_result.get("verified", False),
                    "status": olx_result.get("status"),
                    "is_active": olx_result.get("is_active"),
                    "total_listings": olx_result.get("total_listings")
                }
                
                # Update business record
                if olx_result.get("verified"):
                    business.verified_olx = olx_result.get("is_active", False)
                
                # Log verification attempt
                await self._log_verification(
                    db, business.business_id, "olx", True if olx_result.get("verified") else False, olx_result
                )
            
            except Exception as e:
                logger.warning(f"OLX verification failed for {business.name}: {str(e)}")
                results["verifications"]["olx"] = {"error": str(e)}
        
        # Update external links
        business.external_links = results["external_links"]
        business.last_verification = datetime.utcnow()
        
        # Recalculate trust score
        new_score = self.trust_scorer.calculate_trust_score(
            business=business,
            db=db
        )
        business.trust_score = new_score
        
        # Save changes
        try:
            db.add(business)
            db.commit()
            db.refresh(business)
            results["trust_score"] = business.trust_score
        except Exception as e:
            logger.error(f"Failed to save verification results: {str(e)}")
            db.rollback()
        
        return results
    
    async def _log_verification(
        self,
        db: Session,
        business_id: int,
        api_source: str,
        verified: bool,
        response: Dict
    ):
        """
        Log verification attempt to database
        
        Args:
            db: Database session
            business_id: Business ID
            api_source: Which API performed verification
            verified: Whether verification was successful
            response: API response data
        """
        try:
            log = VerificationLog(
                business_id=business_id,
                api_source=api_source,
                verified=verified,
                response=response,
                verified_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log verification: {str(e)}")
            db.rollback()
    
    async def verify_category(
        self,
        category: str,
        db: Session,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Verify all businesses in a category
        
        Args:
            category: Business category
            db: Database session
            limit: Maximum businesses to verify
        
        Returns:
            Verification summary
        """
        query = db.query(Business).filter(Business.category == category)
        
        if limit:
            query = query.limit(limit)
        
        businesses = query.all()
        
        results = {
            "category": category,
            "total": len(businesses),
            "verified": 0,
            "failed": 0,
            "details": []
        }
        
        for business in businesses:
            try:
                detail = await self.verify_business(business, db)
                results["details"].append(detail)
                
                # Count verified
                if any(v.get("verified") for v in detail.get("verifications", {}).values()):
                    results["verified"] += 1
            
            except Exception as e:
                logger.error(f"Verification failed for {business.name}: {str(e)}")
                results["failed"] += 1
        
        return results
    
    async def verify_all(
        self,
        db: Session
    ) -> Dict:
        """
        Verify all businesses in database
        
        Args:
            db: Database session
        
        Returns:
            Verification summary for all businesses
        """
        businesses = db.query(Business).all()
        
        results = {
            "total": len(businesses),
            "verified": 0,
            "failed": 0,
            "by_category": {}
        }
        
        for business in businesses:
            try:
                detail = await self.verify_business(business, db)
                
                # Track by category
                cat = business.category
                if cat not in results["by_category"]:
                    results["by_category"][cat] = {"verified": 0, "total": 0}
                
                results["by_category"][cat]["total"] += 1
                
                if any(v.get("verified") for v in detail.get("verifications", {}).values()):
                    results["verified"] += 1
                    results["by_category"][cat]["verified"] += 1
            
            except Exception as e:
                logger.error(f"Verification failed: {str(e)}")
                results["failed"] += 1
        
        return results
