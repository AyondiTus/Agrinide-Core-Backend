from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.negotiations import (
    NegotiationStart,
    NegotiationCounter,
    NegotiationResponse,
    NegotiationDetailResponse
)
from app.services import negotiations as nego_service

router = APIRouter()

@router.post("/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def start_negotiation(
    payload: NegotiationStart,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.start_negotiation(db, current_user, payload)

@router.post("/{negotiation_id}/counter", response_model=NegotiationResponse)
async def counter_offer(
    negotiation_id: UUID,
    payload: NegotiationCounter,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.counter_offer(db, current_user, negotiation_id, payload)

@router.post("/{negotiation_id}/accept", response_model=NegotiationResponse)
async def accept_negotiation(
    negotiation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.accept_negotiation(db, current_user, negotiation_id)

@router.post("/{negotiation_id}/reject", response_model=NegotiationResponse)
async def reject_negotiation(
    negotiation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.reject_negotiation(db, current_user, negotiation_id)

@router.get("/", response_model=List[NegotiationResponse])
async def list_negotiations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.list_user_negotiations(db, current_user, skip=skip, limit=limit)

@router.get("/{negotiation_id}", response_model=NegotiationDetailResponse)
async def get_negotiation_detail(
    negotiation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await nego_service.get_negotiation_detail(db, current_user, negotiation_id)
