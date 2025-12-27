import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from functools import wraps

from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.redis = None

    async def hit(self, key: str, limit: int, window: int):
        """Increase the counter fot this key
        if its the first hit, set expiry to window
        """
        current = await self.redis.incr(key)
        if current == 1:
            await self.redis.expire(key, window)

        return current

limiter = RateLimiter()

def rate_limit(limit: int = 5, window: int = 60):
    """Decorator to rate limit any fastapi endpoints
    Args:
        Limit: Maximum number of requests allowed
        Window: time in seconds between each request"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = None # Find request object
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

                if request is None:
                    request = kwargs.get("request")

                if request is None:
                    raise RuntimeError("Request object not found in endpoint")

                # Determine key: per-user or per-Ip
                user = getattr(request.state, "user", None)
                if user:
                    key = f"rl:user:{user['id']}"
                else:
                    client_ip = request.client.host
                    key = f"rl:ip:{client_ip}"

                count = await limiter.hit(key, limit, window)
                if count > limit:
                    ttl = await limiter.redis.ttl(key)
                    raise HTTPException(
                        status_code=HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {ttl}s."
                    )
                return await func(*args, **kwargs)

            return wrapper
        return decorator

# add files