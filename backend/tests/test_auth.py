"""
Test script untuk endpoint Auth (Register Petani, Register Pembeli, & Login).

Jalankan dari root project:
    python tests/test_auth.py
"""
import asyncio
import sys
import os

# Memastikan kita bisa mengimport modul dari root aplikasi
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient, ASGITransport
from main import app
from scripts.get_firebase_token import get_id_token_via_custom_token, create_or_get_user

async def test_auth_flow():
    print(f"{'='*60}")
    print(f"  AUTH INTEGRATION TEST - PETANI & PEMBELI")
    print(f"{'='*60}")
    
    # Ambil credentials dari .env
    email_pembeli = os.getenv("FIREBASE_EMAIL_PEMBELI", "buyer@example.com")
    password_pembeli = os.getenv("FIREBASE_PASSWORD_PEMBELI", "password123")
    
    email_petani = os.getenv("FIREBASE_EMAIL_PETANI", "farmer@example.com")
    password_petani = os.getenv("FIREBASE_PASSWORD_PETANI", "password123")

    # 1. Pastikan user ada di Firebase via Admin SDK
    print("\n[1/5] Setup User Firebase...")
    user_pembeli = create_or_get_user(email_pembeli, "Pembeli Test")
    user_petani = create_or_get_user(email_petani, "Petani Test")
    
    # 2. Ambil Firebase ID Token via Custom Token exchange
    print("\n[2/5] Generating Firebase ID Tokens...")
    token_pembeli, uid_pembeli = get_id_token_via_custom_token(user_pembeli.uid)
    token_petani, uid_petani = get_id_token_via_custom_token(user_petani.uid)

    if not token_pembeli or not token_petani:
        print("  [FAIL] Gagal mendapatkan token dari Firebase. Pastikan FIREBASE_API_KEY valid.")
        return

    print("      [OK] Token berhasil didapatkan.")

    # Inisialisasi ASGI Transport untuk testing langsung ke aplikasi FastAPI tanpa Uvicorn server berjalan
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # 3. Test Endpoint Register Petani
        print("\n[3/5] Testing Endpoint POST /api/v1/auth/register/petani...")
        response_petani = await ac.post(
            "/api/v1/auth/register/petani",
            json={"name": "Bapak Petani Test", "phone": "0811111111"},
            headers={"Authorization": f"Bearer {token_petani}"}
        )
        
        if response_petani.status_code in [200, 201]:
            print("      [OK] Registrasi Petani Berhasil:", response_petani.json()["email"])
        elif response_petani.status_code == 400 and "already registered" in response_petani.text.lower():
            print("      [OK] Petani sudah teregistrasi sebelumnya.")
        else:
            print(f"      [FAIL] Registrasi Petani Gagal: {response_petani.status_code} - {response_petani.text}")
            
        # 4. Test Endpoint Register Pembeli
        print("\n[4/5] Testing Endpoint POST /api/v1/auth/register/pembeli...")
        response_pembeli = await ac.post(
            "/api/v1/auth/register/pembeli",
            json={"name": "Ibu Pembeli Test", "phone": "0822222222"},
            headers={"Authorization": f"Bearer {token_pembeli}"}
        )
        
        if response_pembeli.status_code in [200, 201]:
            print("      [OK] Registrasi Pembeli Berhasil:", response_pembeli.json()["email"])
        elif response_pembeli.status_code == 400 and "already registered" in response_pembeli.text.lower():
            print("      [OK] Pembeli sudah teregistrasi sebelumnya.")
        else:
            print(f"      [FAIL] Registrasi Pembeli Gagal: {response_pembeli.status_code} - {response_pembeli.text}")
            
        # 5. Test Endpoint Login Pembeli
        print("\n[5/5] Testing Endpoint POST /api/v1/auth/login...")
        response_login = await ac.post(
            "/api/v1/auth/login",
            headers={"Authorization": f"Bearer {token_pembeli}"}
        )
        
        if response_login.status_code == 200:
            print("      [OK] Login Berhasil! Role:", response_login.json()["role"])
        else:
            print(f"      [FAIL] Login Gagal: {response_login.status_code} - {response_login.text}")

    print(f"\n{'='*60}")
    print(f"  TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
