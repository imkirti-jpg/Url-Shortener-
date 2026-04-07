from fastapi import FastAPI
from db import create_tables
from project.routes import router as project_router
from Auth.routes import router as auth_router


app = FastAPI()

@app.on_event('startup')
async def on_startup() -> None:
    await create_tables()

app.include_router(auth_router)
app.include_router(project_router)

