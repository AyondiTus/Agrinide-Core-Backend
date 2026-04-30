from fastapi import APIRouter, Depends, UploadFile, File, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.commodities import CommodityCreate, CommodityUpdate, CommodityResponse, BulkInsertResponse
from app.services import commodities as commodity_service

router = APIRouter()

@router.get("/", response_model=List[CommodityResponse])
async def get_all_commodities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Filter by name or location"),
    db: AsyncSession = Depends(get_db)
):
    return await commodity_service.list_commodities(db, skip=skip, limit=limit, search=search)

@router.post("/", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
async def create_commodity(
    commodity: CommodityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await commodity_service.insert_commodity(db, commodity, current_user)

@router.put("/{commodity_id}", response_model=CommodityResponse)
async def update_commodity(
    commodity_id: UUID,
    commodity_update: CommodityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await commodity_service.update_catalog(db, commodity_id, commodity_update, current_user)

@router.post("/bulk", response_model=BulkInsertResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_commodities(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await commodity_service.bulk_insert_excel(db, file, current_user)
