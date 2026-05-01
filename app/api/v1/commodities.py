from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.core.security import get_current_user, RoleChecker
from app.schemas.commodities import CommodityCreate, CommodityUpdate, CommodityResponse, BulkInsertResponse
from app.services import commodities as commodity_service
from app.models.users import User

router = APIRouter()

@router.get("/", response_model=List[CommodityResponse])
async def get_all_commodities(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Filter by name or location"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["farmer", "buyer"]))
):
    return await commodity_service.list_commodities(db, skip=skip, limit=limit, search=search)

@router.post("/", response_model=CommodityResponse, status_code=status.HTTP_201_CREATED)
async def create_commodity(
    name: str = Form(...),
    price_per_kg: float = Form(...),
    current_stock: float = Form(...),
    location: str | None = Form(None),
    is_active: bool = Form(True),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["farmer"]))
):
    commodity = CommodityCreate(
        name=name,
        price_per_kg=price_per_kg,
        current_stock=current_stock,
        location=location,
        is_active=is_active
    )
    return await commodity_service.insert_commodity(db, commodity, image, current_user)

@router.put("/{commodity_id}", response_model=CommodityResponse)
async def update_commodity(
    commodity_id: UUID,
    name: str | None = Form(None),
    price_per_kg: float | None = Form(None),
    current_stock: float | None = Form(None),
    location: str | None = Form(None),
    is_active: bool | None = Form(None),
    image: UploadFile | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["farmer"]))
):
    commodity_update = CommodityUpdate(
        name=name,
        price_per_kg=price_per_kg,
        current_stock=current_stock,
        location=location,
        is_active=is_active
    )
    return await commodity_service.update_catalog(db, commodity_id, commodity_update, image, current_user)

@router.post("/bulk", response_model=BulkInsertResponse, status_code=status.HTTP_201_CREATED)
async def bulk_create_commodities(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker(["farmer"]))
):
    return await commodity_service.bulk_insert_excel(db, file, current_user)
