from fastapi import FastAPI
from db import create_tables
from project.routes import router


app = FastAPI()

@app.on_event('startup')
async def on_startup() -> None:
    await create_tables()
app.include_router(
    router
)