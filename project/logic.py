import json

from project.cache import redis
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from project.models import Click, UrlShortner
from sqlalchemy import select , delete, update
from configure import settings
from datetime import datetime, timedelta, timezone


def base62encoding(number: int) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if number == 0:
        return alphabet[0]
    result = []
    while number > 0:
        remainder = number % 62
        result.append(alphabet[remainder])
        number = number // 62
    return ''.join(result[::-1])

async def shorten(long_url: str, db: AsyncSession):
    new_url = UrlShortner(long_url=long_url, short_url="temp")
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)

    short_code = base62encoding(new_url.id)
    new_url.short_url = short_code
    await db.commit()

    return new_url

async def query(short_code: str, db:AsyncSession):
    cached = await redis.get(f"url:{short_code}")
    if cached:
        data = json.loads(cached)
        return type("URL", (), {
            "id":          data["id"],
            "long_url":    data["long_url"],
            "is_active":   data.get("is_active", True),
            "expires_at":  datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            "max_clicks":  data.get("max_clicks"),
            "click_count": data.get("click_count", 0),
        })()
 
    stmt = select(UrlShortner).where(UrlShortner.short_url == short_code)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()
 
    if url:
        await redis.set(
            f"url:{short_code}",
            json.dumps({
                "id":          url.id,
                "long_url":    url.long_url,
                "is_active":   url.is_active,
                "expires_at":  url.expires_at.isoformat() if url.expires_at else None,
                "max_clicks":  url.max_clicks,
                "click_count": url.click_count,
            }),
            ex=settings.CACHE_TTL,
        )
 
    return url

async def log_click(url_id: int, ip: str | None, user_agent: str | None, referer: str | None):
    """
    Fire-and-forget background task. Opens its own DB session so it runs
    completely independently of the request/response cycle.
    """
    async with SessionLocal() as db:
        click = Click(
            url_id=url_id,
            ip_address=ip,
            user_agent=user_agent,
            referer=referer,
        )
        db.add(click)
        await db.execute(
            update(UrlShortner)
            .where(UrlShortner.id == url_id)
            .values(click_count=UrlShortner.click_count + 1)
        )
        await db.commit()


        url = await db.get(UrlShortner, url_id)
        if url:
            try:
                await redis.set(
                    f"url:{url.short_url}",
                    json.dumps({
                        "id": url.id,
                        "long_url": url.long_url,
                        "is_active": url.is_active,
                        "expires_at": url.expires_at.isoformat() if url.expires_at else None,
                        "max_clicks": url.max_clicks,
                        "click_count": url.click_count,
                    }),
                    ex=settings.CACHE_TTL,
                )
            except Exception:
                pass


async def del_url(db: AsyncSession):
    #calculate 30 days ago
    thirty_days = datetime.now(timezone.utc) - timedelta(days=30)



    stmt = delete(UrlShortner).where(UrlShortner.expires_at != None,
                                     UrlShortner.expires_at<thirty_days)
    
    await db.execute(stmt)
    await db.commit()