from sqlalchemy import String , DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base 
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UrlShortner(Base):
    
    __tablename__ = 'urlshortner'

    id: Mapped[int] = mapped_column(primary_key=True)
    long_url: Mapped[str] = mapped_column(nullable=False)
    short_url: Mapped[str] = mapped_column(nullable=False)

    clicks: Mapped[list["Click"]] = relationship(back_populates="url", cascade="all, delete-orphan")
 
 
class Click(Base):
    __tablename__ = 'clicks'
 
    id: Mapped[int] = mapped_column(primary_key=True)
    url_id: Mapped[int] = mapped_column(ForeignKey('urlshortner.id'), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    referer: Mapped[str | None] = mapped_column(String, nullable=True)
 
    url: Mapped["UrlShortner"] = relationship(back_populates="clicks")

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"