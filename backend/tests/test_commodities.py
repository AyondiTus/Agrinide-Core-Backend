"""
Test script untuk endpoint Commodities (CRUD Komoditas).

Jalankan dari root project:
    python tests/test_commodities.py
"""
import asyncio
import sys
import os

# Memastikan kita bisa mengimport modul dari root aplikasi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient, ASGITransport
from main import app
from scripts.get_firebase_token import get_id_token_via_custom_token, create_or_get_user

async def test_commodities_flow():
    print(f"{'='*60}")
    print(f"  COMMODITIES INTEGRATION TEST - PETANI & PEMBELI")
    print(f"{'='*60}")
    
    # Ambil credentials dari .env
    email_pembeli = os.getenv("FIREBASE_EMAIL_PEMBELI", "buyer@example.com")
    email_petani = os.getenv("FIREBASE_EMAIL_PETANI", "farmer@example.com")

    # 1. Pastikan user ada di Firebase via Admin SDK
    print("\n[1/5] Setup User Firebase...")
    user_pembeli = create_or_get_user(email_pembeli, "Pembeli Test")
    user_petani = create_or_get_user(email_petani, "Petani Test")
    
    # 2. Ambil Firebase ID Token via Custom Token exchange
    print("\n[2/5] Generating Firebase ID Tokens...")
    token_pembeli, uid_pembeli = get_id_token_via_custom_token(user_pembeli.uid)
    token_petani, uid_petani = get_id_token_via_custom_token(user_petani.uid)

    if not token_pembeli or not token_petani:
        print("  [FAIL] Gagal mendapatkan token dari Firebase.")
        return

    print("      [OK] Token berhasil didapatkan.")

    # Inisialisasi ASGI Transport
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        commodity_id = None

        # 3. Test Create Commodity (Hanya Petani)
        print("\n[3/5] Testing Endpoint POST /api/v1/commodities/ (Sebagai Petani)...")
        form_data = {
            "name": "Beras Premium Test",
            "price_per_kg": "15000",
            "current_stock": "100",
            "location": "Malang, Jawa Timur",
            "is_active": "true"
        }
        
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images.jfif")
        
        with open(image_path, "rb") as f:
            files = {"image": ("images.jfif", f, "image/jpeg")}
            response_create = await ac.post(
                "/api/v1/commodities/",
                data=form_data,
                files=files,
                headers={"Authorization": f"Bearer {token_petani}"}
            )
        
        if response_create.status_code == 201:
            data = response_create.json()
            commodity_id = data["id"]
            print(f"      [OK] Komoditas Berhasil Dibuat: {data['name']} (ID: {commodity_id})")
        else:
            print(f"      [FAIL] Gagal Membuat Komoditas: {response_create.status_code} - {response_create.text}")

        # 4. Test Update Commodity (Hanya Petani)
        if commodity_id:
            print(f"\n[4/5] Testing Endpoint PUT /api/v1/commodities/{commodity_id} (Sebagai Petani)...")
            update_data = {
                "name": "Beras Premium Test",
                "price_per_kg": "16000",
                "current_stock": "80",
                "is_active": "false"
            }
            
            with open(image_path, "rb") as f:
                files = {"image": ("images.jfif", f, "image/jpeg")}
                response_update = await ac.put(
                    f"/api/v1/commodities/{commodity_id}",
                    data=update_data,
                    files=files,
                    headers={"Authorization": f"Bearer {token_petani}"}
                )
            
            if response_update.status_code == 200:
                print(f"      [OK] Komoditas Berhasil Diupdate. Harga baru: {response_update.json()['price_per_kg']}")
            else:
                print(f"      [FAIL] Gagal Update Komoditas: {response_update.status_code} - {response_update.text}")

        # 5. Test Get All Commodities (Sebagai Pembeli)
        print("\n[5/5] Testing Endpoint GET /api/v1/commodities/ (Sebagai Pembeli)...")
        response_get = await ac.get(
            "/api/v1/commodities/",
            headers={"Authorization": f"Bearer {token_pembeli}"}
        )
        
        if response_get.status_code == 200:
            items = response_get.json()
            print(f"      [OK] Berhasil Mengambil {len(items)} Komoditas.")
            if len(items) > 0:
                print(f"      Sample: {items[0]['name']} - Rp {items[0]['price_per_kg']}")
        else:
            print(f"      [FAIL] Gagal Mengambil List Komoditas: {response_get.status_code} - {response_get.text}")

    print(f"\n{'='*60}")
    print(f"  TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_commodities_flow())
