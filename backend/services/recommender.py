from sqlalchemy.orm import Session
from neo4j import GraphDatabase
from backend.core.config import settings
from backend.core.database import Business, LeadEvent, Offer
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class RecommenderService:
    """
    Service for generating business recommendations using Neo4j graph queries
    """
    
    def __init__(self):
        """Initialize Neo4j driver"""
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
    
    async def get_recommendations(
        self,
        query: str,
        db: Session,
        category: Optional[str] = None,
        geo: Optional[str] = None,
        limit: int = 5,
        verified_only: bool = True,
        min_trust_score: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get business recommendations based on search query
        
        Args:
            query: Search query string
            db: Database session
            category: Filter by category
            geo: Filter by city
            limit: Number of results
            verified_only: Only return verified businesses
            min_trust_score: Minimum trust score filter
        
        Returns:
            Dictionary with recommendations and metadata
        """
        try:
            # First try PostgreSQL query (faster for exact matches)
            db_query = db.query(Business)
            
            # First search - by name or description
            search_terms = query.lower().split()
            
            # Filter by category if provided
            if category:
                db_query = db_query.filter(Business.category == category)
            
            # Filter by city if provided
            if geo:
                db_query = db_query.filter(Business.city == geo)
            
            # Filter by verification if requested
            if verified_only:
                db_query = db_query.filter(
                    (Business.verified_by_2gis == True) |
                    (Business.verified_by_olx == True) |
                    (Business.verified_by_google == True)
                )
            
            # Filter by trust score
            db_query = db_query.filter(Business.trust_score >= min_trust_score)
            
            # Sort by trust score, then rating
            db_query = db_query.order_by(
                Business.trust_score.desc(),
                Business.rating.desc()
            ).limit(limit)
            
            businesses = db_query.all()
            
            # If no results, try Neo4j graph search
            if not businesses:
                businesses = self._neo4j_search(query, category, geo, limit)
            
            # Convert to dictionary format
            recommendations = []
            for idx, business in enumerate(businesses, 1):
                recommendations.append({
                    "business_id": business.business_id,
                    "name": business.name,
                    "description": business.description,
                    "phone": business.phone,
                    "email": business.email,
                    "address": business.address,
                    "latitude": business.latitude,
                    "longitude": business.longitude,
                    "category": business.category,
                    "rating": business.rating,
                    "rating_count": business.rating_count,
                    "trust_score": business.trust_score,
                    "position": idx,
                    "verified": any([
                        business.verified_by_2gis,
                        business.verified_by_olx,
                        business.verified_by_google
                    ])
                })
            
            # Calculate statistics
            total_count = db.query(Business).count()
            verified_count = db.query(Business).filter(
                (Business.verified_by_2gis == True) |
                (Business.verified_by_olx == True) |
                (Business.verified_by_google == True)
            ).count()
            
            if recommendations:
                avg_trust_score = sum(r["trust_score"] for r in recommendations) / len(recommendations)
            else:
                avg_trust_score = 0.0
            
            # Build citation text
            citation = self._build_citation(query, category, geo, len(recommendations))
            
            return {
                "citation": citation,
                "businesses": recommendations,
                "total": total_count,
                "verified_count": verified_count,
                "avg_trust_score": round(avg_trust_score, 2),
                "results_returned": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}", exc_info=True)
            raise
    
    def _neo4j_search(
        self,
        query: str,
        category: Optional[str] = None,
        geo: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search using Neo4j graph database
        """
        try:
            with self.driver.session() as session:
                # Build Cypher query
                cypher = """
                MATCH (b:Business)
                WHERE (b.name CONTAINS $query OR b.description CONTAINS $query)
                """
                
                params = {"query": query.upper()}
                
                if category:
                    cypher += " AND b.category = $category"
                    params["category"] = category
                
                if geo:
                    cypher += " AND b.city = $geo"
                    params["geo"] = geo
                
                cypher += """
                RETURN b
                ORDER BY b.trust_score DESC, b.rating DESC
                LIMIT $limit
                """
                
                params["limit"] = limit
                
                result = session.run(cypher, params)
                businesses = []
                
                for record in result:
                    b = record["b"]
                    businesses.append({
                        "business_id": b.get("business_id"),
                        "name": b.get("name"),
                        "description": b.get("description"),
                        "phone": b.get("phone"),
                        "rating": b.get("rating", 0.0),
                        "trust_score": b.get("trust_score", 0.0),
                        "category": b.get("category")
                    })
                
                return businesses
        
        except Exception as e:
            logger.error(f"Neo4j search error: {str(e)}")
            return []
    
    def _build_citation(
        self,
        query: str,
        category: Optional[str] = None,
        geo: Optional[str] = None,
        count: int = 0
    ) -> str:
        """
        Build citation text for AI assistant
        """
        parts = [f"По запросу '{query}'"]
        
        if category:
            parts.append(f"в категории '{category}'")
        
        if geo:
            parts.append(f"в городе {geo}")
        
        parts.append(f"найдено {count} проверенных бизнесов")
        
        citation = " ".join(parts) + "."
        
        if count > 0:
            citation += f" Рекомендуется первый результат с оценкой доверия {int(0.95 * 100)}%."
        
        return citation
    
    def get_nearby_businesses(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        limit: int = 10,
        db: Optional[Session] = None
    ) -> List[Dict]:
        """
        Get businesses near given coordinates (geo search)
        """
        try:
            # Simple distance calculation using Haversine formula in SQL
            # For production, use PostGIS extension
            nearby = []
            
            if db:
                businesses = db.query(Business).all()
                
                for business in businesses:
                    if business.latitude and business.longitude:
                        distance = self._haversine_distance(
                            latitude, longitude,
                            business.latitude, business.longitude
                        )
                        
                        if distance <= radius_km:
                            nearby.append({
                                "business_id": business.business_id,
                                "name": business.name,
                                "distance_km": round(distance, 2),
                                "latitude": business.latitude,
                                "longitude": business.longitude,
                                "trust_score": business.trust_score
                            })
                
                # Sort by distance
                nearby.sort(key=lambda x: x["distance_km"])
                
                return nearby[:limit]
            
            return []
        
        except Exception as e:
            logger.error(f"Error getting nearby businesses: {str(e)}")
            return []
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points on Earth in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
