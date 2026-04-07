from sqlalchemy import func, select

from project.models import Click

async def get_total_clicks(db, url_id):
    result = await db.execute(
        select(func.count()).where(Click.url_id == url_id)
    )
    return result.scalar()


async def get_daily_clicks(db, url_id):
    result = await db.execute(
        select(
            func.date(Click.clicked_at),
            func.count()
        )
        .where(Click.url_id == url_id)
        .group_by(func.date(Click.clicked_at))
        .order_by(func.date(Click.clicked_at))
    )

    return [
        {"date": str(row[0]), "count": row[1]}
        for row in result.all()
    ]


async def get_top_referers(db, url_id, limit=10):
    result = await db.execute(
        select(
            Click.referer,
            func.count()
        )
        .where(Click.url_id == url_id, Click.referer.isnot(None))
        .group_by(Click.referer)
        .order_by(func.count().desc())
        .limit(limit)
    )

    return [
        {"referer": row[0] or "Direct", "count": row[1]}
        for row in result.all()
    ]


async def get_top_user_agents(db, url_id, limit=10):
    result = await db.execute(
        select(
            Click.user_agent,
            func.count()
        )
        .where(Click.url_id == url_id, Click.user_agent.isnot(None))
        .group_by(Click.user_agent)
        .order_by(func.count().desc())
        .limit(limit)
    )

    return [
        {"user_agent": row[0], "count": row[1]}
        for row in result.all()
    ]