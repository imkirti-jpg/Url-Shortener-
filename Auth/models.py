from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
from pydantic import BaseModel, EmailStr
from project.models import UrlShortner
