from redis import asyncio as aioredis
from app.core.config import settings
import json
from typing import Any, Optional

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    encoding="utf-8",
    decode_responses=True
)

async def get_cached_data(key: str) -> Optional[Any]:
    """Get data from cache"""
    data = await redis.get(key)
    return json.loads(data) if data else None

async def set_cached_data(key: str, value: Any, expire: int = 300) -> None:
    """Set data in cache with expiration"""
    await redis.set(key, json.dumps(value), ex=expire)

async def invalidate_cache(key: str) -> None:
    """Invalidate cache for a key"""
    await redis.delete(key)

async def clear_cache() -> None:
    """Clear all cache"""
    await redis.flushall() 