from fastapi import Request, HTTPException
from app.core.cache import redis
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: int = 10,
        key_prefix: str = "rate_limit"
    ):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.key_prefix = key_prefix
        self.window_size = 60  # 1 minute window

    async def is_rate_limited(self, request: Request) -> bool:
        """
        Check if the request should be rate limited.
        Uses Redis for distributed rate limiting.
        """
        # Get client IP
        client_ip = request.client.host
        key = f"{self.key_prefix}:{client_ip}"
        
        try:
            # Get current window data
            current = await redis.get(key)
            if not current:
                # First request in window
                await redis.setex(
                    key,
                    self.window_size,
                    f"{time.time()}:{self.burst_size}"
                )
                return False
                
            # Parse window data
            window_start, tokens = current.split(":")
            tokens = int(tokens)
            window_start = float(window_start)
            
            # Check if window has expired
            if time.time() - window_start > self.window_size:
                await redis.setex(
                    key,
                    self.window_size,
                    f"{time.time()}:{self.burst_size}"
                )
                return False
                
            # Check if we have tokens
            if tokens <= 0:
                return True
                
            # Consume a token
            await redis.setex(
                key,
                self.window_size,
                f"{window_start}:{tokens - 1}"
            )
            return False
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Fail open on Redis errors
            return False

# Create rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    if await rate_limiter.is_rate_limited(request):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    return await call_next(request) 