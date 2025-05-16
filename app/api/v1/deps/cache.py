from fastapi import Depends
from app.core.cache import get_cached_data, set_cached_data, invalidate_cache, clear_cache
from typing import Any, Optional, Callable

def get_cache(
    key: str,
    expire: int = 300,
    key_builder: Optional[Callable] = None
):
    """
    Cache dependency factory.
    
    Args:
        key: Cache key
        expire: Cache expiration in seconds
        key_builder: Optional function to build dynamic cache key
        
    Returns:
        Cache dependency function
    """
    async def cache_dependency(
        get_data: Callable,
        *args,
        **kwargs
    ) -> Any:
        # Build cache key if key_builder is provided
        cache_key = key_builder(*args, **kwargs) if key_builder else key
        
        # Try to get from cache
        cached_data = await get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
            
        # If not in cache, get fresh data
        data = await get_data(*args, **kwargs)
        await set_cached_data(cache_key, data, expire)
        return data
        
    return cache_dependency 