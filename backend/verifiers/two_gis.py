"""
2ГИС API Verifier - Verify businesses through 2ГИС catalog
Documentation: https://docs.2gis.com/ru/api
"""

import httpx
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TwoGISVerifier:
    """
    Verify business existence and details through 2ГИС API
    """
    
    def __init__(self, api_key: str):
        """
        Initialize with 2ГИС API key
        
        Args:
            api_key: 2ГИС API key from https://dev.2gis.com/
        """
        self.api_key = api_key
        self.base_url = "https://catalog.api.2gis.com/3.0"
        self.timeout = 30.0
    
    async def verify_business(
        self,
        business_name: str,
        address: Optional[str] = None,
        city: str = "Almaty"
    ) -> Dict:
        """
        Verify business existence in 2ГИС
        
        Args:
            business_name: Name of the business
            address: Street address (optional for better matching)
            city: City name (default: Almaty)
        
        Returns:
            Dictionary with verification result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Build search query
                query = business_name
                if address:
                    query += f", {address}"
                
                params = {
                    "q": query,
                    "city": city,
                    "key": self.api_key,
                    "fields": "items.point,items.address_name,items.rubrics,items.org,items.contact_groups"
                }
                
                response = await client.get(
                    f"{self.base_url}/items",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.warning(f"2GIS API error: {response.status_code}")
                    return {
                        "verified": False,
                        "status": "api_error",
                        "status_code": response.status_code
                    }
                
                data = response.json()
                items = data.get("result", {}).get("items", [])
                
                if not items:
                    return {
                        "verified": False,
                        "status": "not_found",
                        "search_query": query
                    }
                
                # Process first result
                item = items[0]
                
                # Extract contact information if available
                contact_info = {}
                contact_groups = item.get("contact_groups", [])
                for group in contact_groups:
                    for contact in group.get("contacts", []):
                        contact_type = contact.get("type")
                        value = contact.get("value")
                        if contact_type == "phone":
                            contact_info["phone"] = value
                        elif contact_type == "website":
                            contact_info["website"] = value
                        elif contact_type == "email":
                            contact_info["email"] = value
                
                # Extract rubric (category)
                rubrics = item.get("rubrics", [])
                rubric_name = None
                if rubrics:
                    rubric_name = rubrics[0].get("name")
                
                # Get point location
                point = item.get("point", {})
                latitude = point.get("lat")
                longitude = point.get("lon")
                
                return {
                    "verified": True,
                    "status": "found",
                    "name": item.get("name"),
                    "address": item.get("address_name"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "rubric": rubric_name,
                    "2gis_id": item.get("id"),
                    "2gis_url": f"https://2gis.kz/almaty/firm/{item.get('id')}",
                    "contact_info": contact_info,
                    "verified_at": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"2GIS verification error: {str(e)}", exc_info=True)
            return {
                "verified": False,
                "status": "error",
                "error": str(e)
            }
    
    async def get_business_details(
        self,
        business_id: str
    ) -> Dict:
        """
        Get detailed information about business by 2GIS ID
        
        Args:
            business_id: 2GIS business ID
        
        Returns:
            Dictionary with business details
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "id": business_id,
                    "key": self.api_key,
                    "fields": "items.point,items.address_name,items.rubrics,items.rating,items.review_count"
                }
                
                response = await client.get(
                    f"{self.base_url}/items",
                    params=params
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                items = data.get("result", {}).get("items", [])
                
                if not items:
                    return None
                
                item = items[0]
                
                return {
                    "name": item.get("name"),
                    "address": item.get("address_name"),
                    "latitude": item.get("point", {}).get("lat"),
                    "longitude": item.get("point", {}).get("lon"),
                    "rubric": item.get("rubrics", [{}])[0].get("name"),
                    "rating": item.get("rating"),
                    "review_count": item.get("review_count")
                }
        
        except Exception as e:
            logger.error(f"Error getting 2GIS details: {str(e)}")
            return None
    
    async def search_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        limit: int = 10
    ) -> list:
        """
        Search for businesses near coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers
            limit: Maximum results to return
        
        Returns:
            List of nearby businesses
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "location": f"{longitude},{latitude}",
                    "radius": int(radius_km * 1000),  # Convert to meters
                    "key": self.api_key,
                    "fields": "items.point,items.address_name,items.rubrics"
                }
                
                response = await client.get(
                    f"{self.base_url}/items",
                    params=params
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                items = data.get("result", {}).get("items", [])[:limit]
                
                result = []
                for item in items:
                    result.append({
                        "name": item.get("name"),
                        "address": item.get("address_name"),
                        "latitude": item.get("point", {}).get("lat"),
                        "longitude": item.get("point", {}).get("lon"),
                        "2gis_id": item.get("id")
                    })
                
                return result
        
        except Exception as e:
            logger.error(f"Error searching nearby in 2GIS: {str(e)}")
            return []
