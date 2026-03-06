"""
Redis Cache Decorators - Async-safe caching for services
"""

import json
import logging
from typing import Any, Callable, Optional
from functools import wraps
from datetime import timedelta

logger = logging.getLogger(__name__)


def redis_cache(
    ttl_seconds: int = 3600,
    key_prefix: str = ""
):
    """
    Decorator for caching async functions with Redis
    
    Args:
        ttl_seconds: Time to live in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Get Redis client from context if available
            redis_client = kwargs.get("redis_client")
            
            if not redis_client:
                # No Redis available, just call function
                return await func(*args, **kwargs)
            
            try:
                # Build cache key
                cache_key = _build_cache_key(
                    func.__name__,
                    args,
                    kwargs,
                    prefix=key_prefix
                )
                
                # Try to get from cache
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached)
                
                # Cache miss, call function
                result = await func(*args, **kwargs)
                
                # Store in cache
                try:
                    await redis_client.setex(
                        cache_key,
                        ttl_seconds,
                        json.dumps(result)
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache result: {str(e)}")
                
                return result
            
            except Exception as e:
                logger.warning(f"Cache decorator error: {str(e)}")
                # On error, just call function
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def _build_cache_key(
    func_name: str,
    args: tuple,
    kwargs: dict,
    prefix: str = ""
) -> str:
    """
    Build consistent cache key from function name and arguments
    
    Args:
        func_name: Function name
        args: Positional arguments
        kwargs: Keyword arguments
        prefix: Key prefix
    
    Returns:
        Cache key string
    """
    # Remove redis_client and db from key generation
    kwargs_filtered = {k: v for k, v in kwargs.items() 
                      if k not in ["redis_client", "db"]}
    
    # Build key parts
    key_parts = [prefix or "cache", func_name]
    
    # Add args (skip self, db, redis_client)
    for arg in args:
        if arg is not None and not hasattr(arg, "__dict__"):
            key_parts.append(str(arg))
    
    # Add kwargs
    if kwargs_filtered:
        key_parts.append(json.dumps(kwargs_filtered, sort_keys=True))
    
    return ":".join(key_parts)


class CacheInvalidator:
    """
    Manage cache invalidation for related keys
    """
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "cache:recommendation:*")
        """
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {str(e)}")
    
    async def invalidate_business(self, business_id: int):
        """
        Invalidate all caches related to a business
        
        Args:
            business_id: Business ID
        """
        patterns = [
            f"cache:business:{business_id}:*",
            f"cache:recommendation:*:{business_id}:*",
            f"cache:nearby:*"
        ]
        
        for pattern in patterns:
            await self.invalidate_pattern(pattern)
    
    async def invalidate_recommendations(self):
        """Invalidate all recommendation caches"""
        await self.invalidate_pattern("cache:recommendation:*")
    
    async def clear_all(self):
        """Clear entire cache"""
        try:
            await self.redis_client.flushdb()
            logger.info("Cleared all cache")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {str(e)}")


# Cache TTL constants
CACHE_TTL = {
    "short": 300,          # 5 minutes
    "medium": 3600,        # 1 hour
    "long": 86400,         # 24 hours
    "business": 86400,     # Business details - 24 hours
    "recommendation": 3600, # Recommendations - 1 hour
    "nearby": 1800,        # Nearby search - 30 minutes
    "statistics": 7200,    # Statistics - 2 hours
}
