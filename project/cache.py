from redis.asyncio import from_url
from configure import settings

redis = from_url(settings.REDIS_URL, decode_responses=True)