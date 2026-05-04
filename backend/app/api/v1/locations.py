from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.locations import ProvinsiResponse, KotaResponse, KecamatanResponse
from app.repositories import locations as location_repo

router = APIRouter()


@router.get("/provinsi", response_model=List[ProvinsiResponse])
async def get_all_provinsi(db: AsyncSession = Depends(get_db)):
    return await location_repo.get_all_provinsi(db)


@router.get("/provinsi/{provinsi_id}/kota", response_model=List[KotaResponse])
async def get_kota_by_provinsi(provinsi_id: int, db: AsyncSession = Depends(get_db)):
    return await location_repo.get_kota_by_provinsi(db, provinsi_id)


@router.get("/kota/{kota_id}/kecamatan", response_model=List[KecamatanResponse])
async def get_kecamatan_by_kota(kota_id: int, db: AsyncSession = Depends(get_db)):
    return await location_repo.get_kecamatan_by_kota(db, kota_id)
