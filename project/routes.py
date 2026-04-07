from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from project.schema import UrlResponse, UrlRequest, AnalyticsResponse
from project.logic import log_click, shorten, query
from project.service import get_total_clicks, get_daily_clicks, get_top_referers, get_top_user_agents
from Auth.logic import get_current_user

router = APIRouter(prefix='/api')


@router.post('/url_shortner', response_model=UrlResponse, tags=["Api"])
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


@router.get('/analytics/{short_code}', response_model=AnalyticsResponse, tags=["Api"])
async def get_analytics_endpoint(short_code: str, db: AsyncSession = Depends(get_db)):
    url = await query(short_code, db)
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    total_clicks = await get_total_clicks(db, url.id)
    daily_clicks = await get_daily_clicks(db, url.id)
    top_referers = await get_top_referers(db, url.id)
    top_user_agents = await get_top_user_agents(db, url.id)

    return AnalyticsResponse(
        total_clicks=total_clicks,
        daily_clicks=daily_clicks,
        top_referers=top_referers,
        top_user_agents=top_user_agents
    )