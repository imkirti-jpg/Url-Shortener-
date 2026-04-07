from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
from pydantic import BaseModel, EmailStr
from project.models import UrlShortner

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    urlshortners: Mapped[list["UrlShortner"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
