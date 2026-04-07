from sqlalchemy import Boolean, String, DateTime, ForeignKey, func ,Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base 
from datetime import datetime


class UrlShortner(Base):
    
    __tablename__ = 'urlshortner'

    id: Mapped[int] = mapped_column(primary_key=True)
    long_url: Mapped[str] = mapped_column(nullable=False)
    short_url: Mapped[str] = mapped_column(nullable=False)
    custom_alias: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Indexed for faster time-based expiry queries
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    max_clicks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="urlshortners")
    clicks: Mapped[list["Click"]] = relationship(back_populates="url", cascade="all, delete-orphan")
 
 
class Click(Base):
    __tablename__ = 'clicks'
 
    id: Mapped[int] = mapped_column(primary_key=True)
    url_id: Mapped[int] = mapped_column(ForeignKey('urlshortner.id'), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(       DateTime(timezone=True), server_default=func.now())
    ip_address: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    referer: Mapped[str | None] = mapped_column(String, nullable=True)
 
    url: Mapped["UrlShortner"] = relationship(back_populates="clicks")



    
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    urlshortners: Mapped[list["UrlShortner"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
