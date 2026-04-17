from fastapi import FastAPI
from db import create_tables
from project.routes import router as project_router
from Auth.routes import router as auth_router


app = FastAPI(title="LinkSnip Backend")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(project_router)

