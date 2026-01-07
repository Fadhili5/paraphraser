import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from functools import wraps
from collections import defaultdict

from app.core.config import settings


class RateLimiter:
    def __init__(self):
        # key -> (count, expiry_timestamp)
        self.storage: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))

    async def hit(self, key: str, limit: int, window: int):
        now = time.time()
        count, expiry = self.storage[key]

        # reset window if expired
        if now > expiry:
            count = 0
            expiry = now + window

        count += 1
        self.storage[key] = (count, expiry)

        return count, int(expiry - now)


limiter = RateLimiter()


def rate_limit(limit: int = 5, window: int = 60):
    # Disable rate limiting entirely in tests
    if settings.ENV == "test":
        def decorator(func):
            return func
        return decorator

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if request is None:
                request = kwargs.get("request")

            if request is None:
                raise RuntimeError("Request object not found in endpoint")

            user = getattr(request.state, "user", None)
            if user:
                key = f"user:{user['id']}"
            else:
                key = f"ip:{request.client.host}"

            count, ttl = await limiter.hit(key, limit, window)

            if count > limit:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {ttl}s.",
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator