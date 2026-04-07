from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from project.models import User
from db import get_db
from Auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from Auth.service import hash_password, verify_password, create_access_token


router = APIRouter(prefix='/api/auth', tags=["Auth"])


@router.post('/register', response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, password=hash_password(body.password))
    db.add(user)
    await db.commit()

    return TokenResponse(access_token=create_access_token(body.email))


@router.post('/login', response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == body.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(access_token=create_access_token(body.email))
