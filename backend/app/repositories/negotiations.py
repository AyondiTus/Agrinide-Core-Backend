from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_
from uuid import UUID

from app.models.negotiations import Negotiation, NegotiationHistory

async def create_negotiation(db: AsyncSession, data: dict) -> Negotiation:
    negotiation = Negotiation(**data)
    db.add(negotiation)
    await db.commit()
    await db.refresh(negotiation)
    return await get_negotiation_by_id(db, negotiation.id)

async def get_negotiation_by_id(db: AsyncSession, negotiation_id: UUID) -> Negotiation | None:
    query = (
        select(Negotiation)
        .options(
            selectinload(Negotiation.farmer),
            selectinload(Negotiation.buyer),
            selectinload(Negotiation.commodity),
            selectinload(Negotiation.histories),
        )
        .where(Negotiation.id == negotiation_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_negotiations_by_user(
    db: AsyncSession, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 20
):
    query = (
        select(Negotiation)
        .options(
            selectinload(Negotiation.farmer),
            selectinload(Negotiation.buyer),
            selectinload(Negotiation.commodity),
        )
        .where(
            or_(
                Negotiation.farmer_id == user_id,
                Negotiation.buyer_id == user_id
            )
        )
        .order_by(Negotiation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

async def update_negotiation(db: AsyncSession, negotiation: Negotiation, update_data: dict) -> Negotiation:
    for key, value in update_data.items():
        setattr(negotiation, key, value)
    await db.commit()
    await db.refresh(negotiation)
    return negotiation

async def create_history_entry(db: AsyncSession, data: dict) -> NegotiationHistory:
    history = NegotiationHistory(**data)
    db.add(history)
    await db.flush()
    return history

async def get_negotiation_histories(db: AsyncSession, negotiation_id: UUID):
    query = (
        select(NegotiationHistory)
        .where(NegotiationHistory.negotiation_id == negotiation_id)
        .order_by(NegotiationHistory.created_at.asc())
    )
    result = await db.execute(query)
    return result.scalars().all()
