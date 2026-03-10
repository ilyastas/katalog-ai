"""
Import business data from Katalog-AI GitHub Pages to local database.
"""

import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, Business, init_db

logger = logging.getLogger(__name__)


async def import_data_from_katalog_ai(db: Session = None) -> dict:
    """
    Import the canonical company registry from Katalog-AI and populate the database.
    """
    if db is None:
        db = SessionLocal()

    try:
        init_db()
        stats = {
            "businesses_imported": 0,
            "offers_imported": 0,
            "errors": [],
        }

        url = "https://ilyastas.github.io/katalog-ai/data/companies.json"
        logger.info(f"Importing canonical companies from {url}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()

        for item in payload.get("companies", []):
            item_id = item.get("id")
            if not item_id:
                continue

            existing = db.query(Business).filter(Business.business_id == item_id).first()
            if existing:
                logger.info(f"Business {item_id} already exists, skipping")
                continue

            verification_sources = set(item.get("verification", {}).get("sources", []))
            metrics = item.get("metrics", {})

            business = Business(
                business_id=item_id,
                name=item.get("name", ""),
                description=item.get("description"),
                category=item.get("category"),
                phone=item.get("contact", {}).get("phone"),
                email=item.get("contact", {}).get("email"),
                website=item.get("website") or item.get("url"),
                address=item.get("geo"),
                city=item.get("city"),
                latitude=None,
                longitude=None,
                rating=float(metrics.get("rating", 0.0) or 0.0),
                rating_count=0,
                verified_by_2gis=False,
                verified_by_olx=False,
                verified_by_google=("google" in verification_sources),
                trust_score=1.0 if item.get("verification", {}).get("status") == "verified" else 0.0,
                last_verified=datetime.utcnow(),
                external_links={"sameAs": item.get("same_as", [])},
                tracking_codes={"keywords": item.get("keywords", [])},
            )

            db.add(business)
            stats["businesses_imported"] += 1
            logger.info(f"Imported business: {business.name}")

        db.commit()
        logger.info(f"Import completed: {stats}")
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
    result = asyncio.run(import_data_from_katalog_ai())

    print("\n" + "=" * 50)
    print("IMPORT RESULTS")
    print("=" * 50)
    print(f"Businesses imported: {result['businesses_imported']}")
    print(f"Offers imported: {result['offers_imported']}")
    if result["errors"]:
        print(f"Errors: {len(result['errors'])}")
        for error in result["errors"]:
            print(f"  - {error}")
    print("=" * 50)