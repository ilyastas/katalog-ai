"""
Google Places Verifier - Verify businesses through Google Places API
Documentation: https://developers.google.com/maps/documentation/places/web-service/overview
"""

import httpx
from typing import Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GooglePlacesVerifier:
    """
    Verify business information through Google Places API
    """
    
    def __init__(self, api_key: str):
        """
        Initialize with Google Places API key
        
        Args:
            api_key: Google Places API key from Google Cloud Console
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.timeout = 30.0
    
    async def search_business(
        self,
        business_name: str,
        address: Optional[str] = None,
        location: Optional[tuple] = None  # (latitude, longitude)
    ) -> Dict:
        """
        Search for business in Google Places
        
        Args:
            business_name: Name of the business
            address: Street address (optional)
            location: Coordinates tuple (lat, lng) for nearby search
        
        Returns:
            Dictionary with search result
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                query = business_name
                if address:
                    query += f", {address}"
                
                params = {
                    "query": query,
                    "key": self.api_key
                }
                
                # Use nearby search if coordinates provided
                if location:
                    params["location"] = f"{location[0]},{location[1]}"
                    params["radius"] = 5000  # 5km radius
                    endpoint = f"{self.base_url}/nearbysearch/json"
                else:
                    endpoint = f"{self.base_url}/textsearch/json"
                
                response = await client.get(endpoint, params=params)
                
                if response.status_code != 200:
                    logger.warning(f"Google Places API error: {response.status_code}")
                    return {
                        "verified": False,
                        "status": "api_error",
                        "status_code": response.status_code
                    }
                
                data = response.json()
                
                if data.get("status") == "ZERO_RESULTS":
                    return {
                        "verified": False,
                        "status": "not_found",
                        "search_query": query
                    }
                
                if data.get("status") != "OK":
                    return {
                        "verified": False,
                        "status": data.get("status"),
                        "search_query": query
                    }
                
                results = data.get("results", [])
                if not results:
                    return {
                        "verified": False,
                        "status": "no_results"
                    }
                
                # Get first result details
                place = results[0]
                place_id = place.get("place_id")
                
                # Get detailed information
                details = await self.get_place_details(place_id)
                
                if details:
                    return {
                        "verified": True,
                        "status": "found",
                        **details
                    }
                else:
                    return {
                        "verified": True,
                        "status": "found",
                        "name": place.get("name"),
                        "address": place.get("formatted_address"),
                        "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                        "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                        "place_id": place_id,
                        "google_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        "verified_at": datetime.utcnow().isoformat()
                    }
        
        except Exception as e:
            logger.error(f"Google Places verification error: {str(e)}", exc_info=True)
            return {
                "verified": False,
                "status": "error",
                "error": str(e)
            }
    
    async def get_place_details(
        self,
        place_id: str
    ) -> Optional[Dict]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Places ID
        
        Returns:
            Dictionary with place details or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "place_id": place_id,
                    "fields": "formatted_address,name,geometry,rating,review_count,formatted_phone_number,website,opening_hours,photos",
                    "key": self.api_key
                }
                
                response = await client.get(
                    f"{self.base_url}/details/json",
                    params=params
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if data.get("status") != "OK":
                    return None
                
                result = data.get("result", {})
                
                return {
                    "name": result.get("name"),
                    "address": result.get("formatted_address"),
                    "latitude": result.get("geometry", {}).get("location", {}).get("lat"),
                    "longitude": result.get("geometry", {}).get("location", {}).get("lng"),
                    "rating": result.get("rating"),
                    "review_count": result.get("user_ratings_total"),
                    "phone": result.get("formatted_phone_number"),
                    "website": result.get("website"),
                    "place_id": place_id,
                    "google_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    "is_open": result.get("opening_hours", {}).get("open_now"),
                    "verified_at": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error getting Google place details: {str(e)}")
            return None
    
    async def verify_by_coordinates(
        self,
        latitude: float,
        longitude: float,
        radius_meters: int = 100
    ) -> Dict:
        """
        Find businesses at specific coordinates
        
        Args:
            latitude: Latitude
            longitude: Longitude
            radius_meters: Search radius in meters
        
        Returns:
            List of businesses at location
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "location": f"{latitude},{longitude}",
                    "radius": radius_meters,
                    "key": self.api_key
                }
                
                response = await client.get(
                    f"{self.base_url}/nearbysearch/json",
                    params=params
                )
                
                if response.status_code != 200:
                    return {"verified": False, "status": "api_error"}
                
                data = response.json()
                
                if data.get("status") != "OK":
                    return {
                        "verified": False,
                        "status": data.get("status")
                    }
                
                results = data.get("results", [])
                
                businesses = []
                for result in results:
                    businesses.append({
                        "name": result.get("name"),
                        "address": result.get("vicinity"),
                        "latitude": result.get("geometry", {}).get("location", {}).get("lat"),
                        "longitude": result.get("geometry", {}).get("location", {}).get("lng"),
                        "rating": result.get("rating"),
                        "place_id": result.get("place_id")
                    })
                
                return {
                    "verified": True,
                    "status": "found",
                    "businesses": businesses,
                    "verified_at": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error in coordinate verification: {str(e)}")
            return {"verified": False, "status": "error", "error": str(e)}
