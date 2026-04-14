from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re

class UrlResponse(BaseModel):
    short_url: str
    long_url: str
    custom_alias: Optional[str] = None

    class Config:
        from_attributes = True 

class UrlRequest(BaseModel):
    long_url: str
    custom_alias: Optional[str] = Field(None, max_length=50)
    
    @field_validator('custom_alias')
    @classmethod
    def validate_alias(cls, v):
        if v is None or v.strip() == "":
            return None  # treat empty as no alias

        if not re.match(r'^[a-zA-Z0-9_-]{1,50}$', v):
            raise ValueError(
                'Alias must contain only alphanumeric characters, hyphens, and underscores (1-50 chars)'
            )

        reserved = {'api', 'admin', 'analytics', 'auth', 'user', 'login', 'logout', 'register'}
        if v.lower() in reserved:
            raise ValueError(f'Alias "{v}" is reserved and cannot be used')

        return v
    
class DailyClick(BaseModel):
    date: str
    count: int

class RefererStat(BaseModel):
    referer: str
    count: int

class UserAgentStat(BaseModel):
    user_agent: str
    count: int

class AnalyticsResponse(BaseModel):
    total_clicks: int
    daily_clicks: List[DailyClick]
    top_referers: List[RefererStat]
    top_user_agents: List[UserAgentStat]