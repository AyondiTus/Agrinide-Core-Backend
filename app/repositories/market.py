from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date

from app.models.market import MarketPrice, MarketPriceDaily

async def get_or_create_market_price(db: AsyncSession, market_price_id: str, name: str, unit: str) -> MarketPrice:
    query = select(MarketPrice).where(MarketPrice.id == market_price_id)
    result = await db.execute(query)
    mp = result.scalars().first()
    
    if not mp:
        mp = MarketPrice(id=market_price_id, name=name, unit=unit)
        db.add(mp)
        await db.flush()
        
    return mp

async def upsert_market_price_daily(
    db: AsyncSession, 
    market_price_id: str, 
    date_obj: date, 
    current_price: int, 
    previous_price: int, 
    change_rp: int, 
    change_percentage: float, 
    trend: str
) -> MarketPriceDaily:
    
    query = select(MarketPriceDaily).where(
        MarketPriceDaily.market_price_id == market_price_id,
        MarketPriceDaily.date == date_obj
    )
    result = await db.execute(query)
    existing_daily = result.scalars().first()
    
    if existing_daily:
        existing_daily.current_price = current_price
        existing_daily.previous_price = previous_price
        existing_daily.change_rp = change_rp
        existing_daily.change_percentage = change_percentage
        existing_daily.trend = trend
        return existing_daily
    else:
        daily = MarketPriceDaily(
            market_price_id=market_price_id,
            date=date_obj,
            current_price=current_price,
            previous_price=previous_price,
            change_rp=change_rp,
            change_percentage=change_percentage,
            trend=trend
        )
        db.add(daily)
        return daily
