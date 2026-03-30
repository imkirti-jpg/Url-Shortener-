from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from project.models import Click, UrlShortner
from sqlalchemy import select

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from project.service import decode_token
import jwt


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
    stmt = select(UrlShortner).where(UrlShortner.short_url == short_code)
    result = await db.execute(stmt)
    url = result.scalar_one_or_none()
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
        await db.commit()
 

bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    try:
        payload = decode_token(credentials.credentials)
        return payload["sub"]  # email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
