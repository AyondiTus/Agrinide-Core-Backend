from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.scheduler import init_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to Agrinide Core Backend API"}

from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
