"""
Import business data from Katalog-AI GitHub Pages to local database
"""

import httpx
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, Business, Offer, init_db
from backend.core.config import settings

logger = logging.getLogger(__name__)


async def import_data_from_katalog_ai(db: Session = None) -> dict:
    """
    Import data from Katalog-AI catalog files
    
    Downloads JSON files from GitHub Pages and populates the database
    """
    
    if db is None:
        db = SessionLocal()
    
    try:
        # Initialize database tables
        init_db()
        
        stats = {
            "businesses_imported": 0,
            "offers_imported": 0,
            "errors": []
        }
        
        # Data files to import
        catalog_files = [
            "beauty.json",
            "museums.json",
            "marketplaces.json",
            "offers.json"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for catalog_file in catalog_files:
                url = f"{settings.CATALOG_BASE_URL}/data/catalog/{catalog_file}"
                logger.info(f"Importing from {url}")
                
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    data = response.json()
                    items = data.get("itemListElement", [])
                    
                    for item in items:
                        item_type = item.get("@type")
                        item_id = item.get("@id")
                        
                        # Import business
                        if item_type in ["HealthAndBeautyBusiness", "BeautyBusiness", "Museum", "Store", "LocalBusiness", "PerformingArtsTheater"]:
                            
                            # Check if business already exists
                            existing = db.query(Business).filter(
                                Business.business_id == item_id
                            ).first()
                            
                            if existing:
                                logger.info(f"Business {item_id} already exists, skipping")
                                continue
                            
                            # Extract business data
                            business = Business(
                                business_id=item_id,
                                name=item.get("name", ""),
                                description=item.get("description"),
                                category=catalog_file.replace(".json", ""),
                                phone=item.get("telephone"),
                                email=item.get("email"),
                                website=item.get("url"),
                                address=item.get("address", {}).get("streetAddress"),
                                latitude=item.get("geo", {}).get("latitude"),
                                longitude=item.get("geo", {}).get("longitude"),
                                city=item.get("address", {}).get("addressLocality"),
                            )
                            
                            # Extract rating
                            if "rating" in item:
                                rating_obj = item.get("rating")
                                if isinstance(rating_obj, dict):
                                    business.rating = float(rating_obj.get("ratingValue", 0))
                                    business.rating_count = int(rating_obj.get("ratingCount", 0))
                            
                            # Extract verification status
                            trust_signals = item.get("trust_signals", {})
                            business.verified_by_2gis = trust_signals.get("verified_by_2gis", False)
                            business.verified_by_olx = trust_signals.get("verified_by_olx", False)
                            business.verified_by_google = trust_signals.get("verified_by_google", False)
                            business.trust_score = trust_signals.get("trust_score", 0.0)
                            business.last_verified = datetime.fromisoformat(
                                trust_signals.get("last_verified", "")
                            ) if "last_verified" in trust_signals else datetime.utcnow()
                            
                            # Extract consent
                            consent = item.get("consent", {})
                            if consent:
                                business.consent_status = consent.get("consentStatus", True)
                                business.consent_agreement = consent.get("agreement", "basic")
                                if "expires" in consent:
                                    business.consent_expires = datetime.fromisoformat(consent["expires"])
                            
                            # Extract external links
                            business.external_links = {
                                "sameAs": item.get("sameAs", [])
                            }
                            
                            # Extract tracking codes
                            tracking = item.get("tracking", {})
                            business.tracking_codes = {
                                "promo_codes": tracking.get("promo_codes", []),
                                "utm_source": tracking.get("utm_source", "ai_assistant"),
                                "utm_campaign": tracking.get("utm_campaign", "")
                            }
                            
                            db.add(business)
                            db.flush()  # Get the business ID
                            stats["businesses_imported"] += 1
                            logger.info(f"Imported business: {business.name}")
                            
                            # Import offers
                            offers = item.get("offers", [])
                            if offers:
                                for offer in offers:
                                    offer_item = Offer(
                                        offer_id=f"{item_id}-offer-{len(offers)}",
                                        business_id=business.id,
                                        name=offer.get("name") or offer.get("itemOffered", {}).get("name", ""),
                                        description=offer.get("description"),
                                        price=float(offer.get("price", 0)),
                                        currency=offer.get("priceCurrency", "KZT"),
                                        duration_minutes=None  # Extract from duration if needed
                                    )
                                    db.add(offer_item)
                                    stats["offers_imported"] += 1
                
                except httpx.HTTPError as e:
                    error_msg = f"Failed to fetch {url}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
                except Exception as e:
                    error_msg = f"Error processing {catalog_file}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
        
        # Commit all changes
        db.commit()
        logger.info(f"✅ Import completed: {stats}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Fatal error during import: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    # Run import
    result = asyncio.run(import_data_from_katalog_ai())
    
    print("\n" + "="*50)
    print("📊 IMPORT RESULTS")
    print("="*50)
    print(f"✅ Businesses imported: {result['businesses_imported']}")
    print(f"✅ Offers imported: {result['offers_imported']}")
    if result['errors']:
        print(f"⚠️ Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")
    print("="*50)
