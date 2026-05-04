from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.models.commodities import Commodity
from app.schemas.commodities import CommodityCreate, CommodityUpdate

async def get_commodities(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: str | None = None
):
    query = select(Commodity).options(selectinload(Commodity.farmer)).where(Commodity.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Commodity.name.ilike(search_term),
                Commodity.location.ilike(search_term)
            )
        )
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_commodity_by_id(db: AsyncSession, commodity_id: UUID):
    query = select(Commodity).options(selectinload(Commodity.farmer)).where(Commodity.id == commodity_id)
    result = await db.execute(query)
    return result.scalars().first()

async def create_commodity(db: AsyncSession, commodity: CommodityCreate, farmer_id: str):
    db_commodity = Commodity(
        farmer_id=farmer_id,
        name=commodity.name,
        price_per_kg=commodity.price_per_kg,
        current_stock=commodity.current_stock,
        location=commodity.location,
        is_active=commodity.is_active
    )
    db.add(db_commodity)
    await db.commit()
    await db.refresh(db_commodity)
    
    # Reload with farmer info
    return await get_commodity_by_id(db, db_commodity.id)

async def update_commodity(db: AsyncSession, db_commodity: Commodity, commodity_update: CommodityUpdate):
    update_data = commodity_update.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(db_commodity, key, value)
        
    await db.commit()
    await db.refresh(db_commodity)
    return db_commodity

async def bulk_create_commodities(db: AsyncSession, commodities_data: list[dict]):
    db_commodities = []
    for item in commodities_data:
        db_commodity = Commodity(**item)
        db_commodities.append(db_commodity)
        
    db.add_all(db_commodities)
    await db.flush()
    return len(db_commodities)
