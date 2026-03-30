from fastapi import APIRouter, Depends, HTTPException , BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import jwt

from db import get_db
from project.schema import UrlResponse, UrlRequest
from project.logic import log_click, shorten, query, get_current_user
from project.models import User, RegisterRequest, LoginRequest, TokenResponse
from project.service import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/api')

# URL Shortener 

@router.post('/url_shortner', response_model=UrlResponse,tags=["Api"])
async def url_shorten_endpoint(
    data: UrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)   # protected
):
    return await shorten(data.long_url, db)

@router.get('/{short_code}', tags=["Api"])
async def get_code_endpoint(short_code: str, request: Request,
    background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    url = await query(short_code, db)
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    
    # Extract request metadata
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")
 
    # Schedule the DB write — runs after the response is sent
    background_tasks.add_task(log_click, url.id, ip, user_agent, referer)
 
    return RedirectResponse(url=url.long_url, status_code=307)

# Auth 

@router.post('/auth/register', response_model=TokenResponse, tags=["Auth"])
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, password=hash_password(body.password))
    db.add(user)
    await db.commit()

    return TokenResponse(access_token=create_access_token(body.email))

@router.post('/auth/login', response_model=TokenResponse, tags=["Auth"])
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(access_token=create_access_token(body.email))