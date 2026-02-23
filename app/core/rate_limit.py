import asyncio
import time
from contextlib import asynccontextmanager
from functools import wraps

from fastapi import Request, HTTPException, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

from app.core.config import settings


class RateLimiter:
    def __init__(self, cleanup_interval: int = 300):
        # key -> (count, expiry_timestamp)
        self.storage: dict[str, tuple[int, float]] = {}
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    def start(self):
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def stop(self):
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(self._cleanup_interval)
            now = time.time()
            async with self._lock:
                expired = [k for k, (_, expiry) in self.storage.items() if now > expiry]
                for k in expired:
                    del self.storage[k]

    async def hit(self, key: str, limit: int, window: int) -> tuple[int, int]:
        now = time.time()
        async with self._lock:
            count, expiry = self.storage.get(key, (0, 0.0))

            if now > expiry:
                count = 0
                expiry = now + window

            count += 1
            self.storage[key] = (count, expiry)

        return count, int(expiry - now)


limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app):
    limiter.start()
    yield
    limiter.stop()


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

            if request.method == "OPTIONS":
                return Response(status_code=204)

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