from fastapi import HTTPException, Request

from project.cache import redis


def _rate_limit_identity(request: Request) -> str | None:
    # Identity source for rate limiting.
    api_key = request.headers.get("x-api-key")
    if api_key:
        return f"api:{api_key.strip()}"

    # fallback to IP for public routes
    ip = request.client.host if request.client else "anonymous"
    return f"ip:{ip}"


def rate_limit(scope: str, limit: int, window_seconds: int):
    async def _limit(request: Request):
        identity = _rate_limit_identity(request)
        if not identity:
            raise HTTPException(
                status_code=400,
                detail="Missing API key. Provide X-API-Key header.",
            )

        key = f"rl:{scope}:{identity}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, window_seconds)

        if count > limit:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Retry in {max(ttl, 1)}s",
            )

    return _limit
