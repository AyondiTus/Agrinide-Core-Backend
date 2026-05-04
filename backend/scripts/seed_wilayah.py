"""
Script untuk mengisi data wilayah Jawa Timur (Provinsi, Kota, Kecamatan)
dari API EMSIFA ke PostgreSQL.

Cara menjalankan (dari folder backend/):
    python scripts/seed_wilayah.py
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models.locations import Provinsi, Kota, Kecamatan

BASE_URL = "https://www.emsifa.com/api-wilayah-indonesia/api"

# Hanya seed Jawa Timur
TARGET_PROVINSI_ID = "35"
TARGET_PROVINSI_NAME = "JAWA TIMUR"


async def fetch_json(client: httpx.AsyncClient, url: str) -> list:
    try:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[!] Gagal fetch {url}: {e}")
        return []


async def run_seeder():
    async with httpx.AsyncClient() as client:
        async with AsyncSessionLocal() as session:

            # ── 1. Simpan Provinsi Jawa Timur ────────────────────────────────
            print(f"[*] Menyimpan provinsi {TARGET_PROVINSI_NAME} (ID: {TARGET_PROVINSI_ID})...")
            stmt = pg_insert(Provinsi).values(
                id=int(TARGET_PROVINSI_ID),
                provinsi_name=TARGET_PROVINSI_NAME
            ).on_conflict_do_nothing(index_elements=["id"])
            await session.execute(stmt)
            await session.commit()
            print(f"[+] Provinsi {TARGET_PROVINSI_NAME} disimpan.")

            # ── 2. Fetch & Simpan Kota Jawa Timur ────────────────────────────
            print(f"[*] Fetching data kota untuk Jawa Timur...")
            kota_data = await fetch_json(client, f"{BASE_URL}/regencies/{TARGET_PROVINSI_ID}.json")

            kota_ids = []
            for kota in kota_data:
                stmt = pg_insert(Kota).values(
                    id=int(kota["id"]),
                    provinsi_id=int(kota["province_id"]),
                    kota_name=kota["name"]
                ).on_conflict_do_nothing(index_elements=["id"])
                await session.execute(stmt)
                kota_ids.append(kota["id"])
                print(f"  [+] {kota['name']}")

            await session.commit()
            print(f"[+] {len(kota_ids)} kota Jawa Timur disimpan.")

            # ── 3. Fetch & Simpan Kecamatan per Kota ─────────────────────────
            print(f"[*] Fetching kecamatan untuk {len(kota_ids)} kota...")
            total_kecamatan = 0

            for i, kota_id in enumerate(kota_ids):
                print(f"  [~] Fetching kecamatan kota ID {kota_id} ({i+1}/{len(kota_ids)})...")
                kecamatan_data = await fetch_json(client, f"{BASE_URL}/districts/{kota_id}.json")

                for kec in kecamatan_data:
                    stmt = pg_insert(Kecamatan).values(
                        id=int(kec["id"]),
                        kota_id=int(kec["regency_id"]),
                        kecamatan_name=kec["name"]
                    ).on_conflict_do_nothing(index_elements=["id"])
                    await session.execute(stmt)

                total_kecamatan += len(kecamatan_data)
                await session.commit()
                await asyncio.sleep(0.1)

            print(f"[+] Total {total_kecamatan} kecamatan disimpan.")

    print("\n✅ Seeder Jawa Timur selesai!")


if __name__ == "__main__":
    asyncio.run(run_seeder())
