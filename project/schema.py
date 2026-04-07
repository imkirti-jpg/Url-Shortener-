from pydantic import BaseModel
from typing import List

class UrlResponse(BaseModel):
    short_url: str
    long_url: str

class UrlRequest(BaseModel):
    long_url: str

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