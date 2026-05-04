from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.locations import Provinsi, Kota, Kecamatan


async def get_all_provinsi(db: AsyncSession):
    result = await db.execute(select(Provinsi).order_by(Provinsi.provinsi_name))
    return result.scalars().all()


async def get_kota_by_provinsi(db: AsyncSession, provinsi_id: int):
    result = await db.execute(
        select(Kota).where(Kota.provinsi_id == provinsi_id).order_by(Kota.kota_name)
    )
    return result.scalars().all()


async def get_kecamatan_by_kota(db: AsyncSession, kota_id: int):
    result = await db.execute(
        select(Kecamatan).where(Kecamatan.kota_id == kota_id).order_by(Kecamatan.kecamatan_name)
    )
    return result.scalars().all()
