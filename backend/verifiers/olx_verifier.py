"""
OLX Verifier - Verify seller activity on OLX through Apify
Uses: https://apify.com/drobnikj/olx-scraper (free tier available)
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OLXVerifier:
    """
    Verify seller activity and credibility on OLX platform
    """
    
    def __init__(self, apify_token: str):
        """
        Initialize with Apify token for OLX scraping
        
        Args:
            apify_token: Token from https://apify.com/
        """
        self.apify_token = apify_token
        self.actor_id = "drobnikj/olx-scraper"
        
        # Only initialize if token is provided
        if not apify_token or apify_token == "":
            logger.warning("Apify token not provided - OLX verification disabled")
            self.client = None
            return
        
        try:
            from apify_client import ApifyClient
            self.client = ApifyClient(apify_token)
        except ImportError:
            logger.warning("apify-client not installed - OLX verification disabled")
            self.client = None
    
    async def verify_seller(
        self,
        profile_url: str
    ) -> Dict:
        """
        Verify seller on OLX by profile URL
        
        Args:
            profile_url: OLX seller profile URL
        
        Returns:
            Dictionary with verification result
        """
        if not self.client:
            return {
                "verified": False,
                "status": "disabled",
                "reason": "Apify client not configured"
            }
        
        try:
            # Validate URL
            if not profile_url or "olx.kz" not in profile_url:
                return {
                    "verified": False,
                    "status": "invalid_url",
                    "profile_url": profile_url
                }
            
            # Run Apify actor to scrape seller profile
            run_input = {
                "profileUrls": [profile_url],
                "maxItems": 20,  # Get last 20 listings
                "proxyConfiguration": {
                    "useApifyProxy": True
                }
            }
            
            # Execute scraping (non-blocking in production via Celery)
            try:
                run = self.client.actor(self.actor_id).call(run_input=run_input)
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
                
                if not items:
                    return {
                        "verified": False,
                        "status": "no_listings",
                        "profile_url": profile_url
                    }
                
                # Analyze seller activity
                total_listings = len(items)
                
                # Get dates for recency check
                dates = []
                for item in items:
                    if "postedDate" in item:
                        dates.append(item["postedDate"])
                
                # Check if seller is active (has listings in last 30 days)
                from datetime import datetime, timedelta
                now = datetime.utcnow()
                thirty_days_ago = now - timedelta(days=30)
                
                recent_count = 0
                if dates:
                    for date_str in dates:
                        try:
                            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            if date > thirty_days_ago:
                                recent_count += 1
                        except:
                            pass
                
                is_active = recent_count > 0
                
                return {
                    "verified": True,
                    "status": "found",
                    "is_active": is_active,
                    "total_listings": total_listings,
                    "recent_listings_30d": recent_count,
                    "last_listing_date": dates[0] if dates else None,
                    "profile_url": profile_url,
                    "verified_at": datetime.utcnow().isoformat(),
                    "source": "olx"
                }
            
            except Exception as e:
                logger.warning(f"Apify scraping error: {str(e)}")
                return {
                    "verified": False,
                    "status": "scrape_error",
                    "error": str(e),
                    "profile_url": profile_url
                }
        
        except Exception as e:
            logger.error(f"OLX verification error: {str(e)}", exc_info=True)
            return {
                "verified": False,
                "status": "error",
                "error": str(e)
            }
    
    async def check_seller_ratings(
        self,
        profile_url: str
    ) -> Dict:
        """
        Get seller ratings and reviews from OLX
        
        Args:
            profile_url: OLX seller profile URL
        
        Returns:
            Dictionary with rating information
        """
        if not self.client:
            return {"status": "disabled"}
        
        try:
            # This would require additional scraping/parsing
            # For now, return placeholder
            return {
                "status": "available_with_advanced_scraping",
                "note": "Requires advanced Apify actor configuration"
            }
        
        except Exception as e:
            logger.error(f"Error getting OLX ratings: {str(e)}")
            return {"error": str(e)}
