from fastapi import APIRouter
from app.api.v1 import auth, commodities, negotiations

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(commodities.router, prefix="/commodities", tags=["commodities"])
api_router.include_router(negotiations.router, prefix="/negotiations", tags=["negotiations"])
