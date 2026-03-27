from configure import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


#  Async engine (correct function)
engine = create_async_engine(
    config.DATABASE_URL,
    echo=True,
)


#  Async session factory (modern way)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base model
class Base(DeclarativeBase):
    pass


#  Dependency
async def get_db():
    async with SessionLocal() as db:
        yield db


# Create tables (fixed typo + name)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)