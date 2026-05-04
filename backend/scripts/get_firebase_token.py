"""
Script untuk mendapatkan Firebase ID Token untuk testing (Pembeli & Petani).
Menggunakan Firebase Admin SDK Custom Token (tanpa password).

Jalankan dari root project:
    python scripts/get_firebase_token.py
"""
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load app config dan inisialisasi Firebase Admin SDK
from app.core.config import settings
import app.core.security  # noqa: F401
from firebase_admin import auth as admin_auth
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

def create_or_get_user(email, display_name="Test User"):
    """Buat user baru atau ambil yang sudah ada via Admin SDK."""
    try:
        user = admin_auth.get_user_by_email(email)
        print(f"  [INFO] User sudah ada: {email} (UID: {user.uid})")
        return user
    except admin_auth.UserNotFoundError:
        user = admin_auth.create_user(
            email=email,
            display_name=display_name
        )
        print(f"  [OK] User baru dibuat: {email} (UID: {user.uid})")
        return user

def get_id_token_via_custom_token(uid):
    """Buat custom token dari Admin SDK, lalu tukarkan ke ID Token via REST API."""
    # Step 1: Buat custom token
    custom_token = admin_auth.create_custom_token(uid)
    custom_token_str = custom_token.decode("utf-8") if isinstance(custom_token, bytes) else custom_token
    
    # Step 2: Tukarkan custom token ke ID Token
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_API_KEY}"
    payload = {
        "token": custom_token_str,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if response.status_code == 200:
        return data.get("idToken"), uid
    else:
        error_msg = data.get("error", {}).get("message", "Unknown error")
        print(f"  [FAIL] Token exchange gagal: {error_msg}")
        return None, None

def print_token_info(role, email, uid, token):
    if token:
        print(f"\n{'='*60}")
        print(f"  TOKEN BERHASIL DIDAPATKAN - {role.upper()}")
        print(f"{'='*60}")
        print(f"  Role  : {role}")
        print(f"  UID   : {uid}")
        print(f"  Email : {email}")
        print(f"\n  ID Token (copy ke Bruno/Postman):")
        print(f"  {'-'*55}")
        print(f"  {token}")
        print(f"  {'-'*55}")
        print(f"\n  Token berlaku selama 1 jam.")
        print(f"{'='*60}\n")

def main():
    if not FIREBASE_API_KEY:
        print("[ERROR] FIREBASE_API_KEY belum diset di .env!")
        return
    
    print(f"{'='*60}")
    print(f"  FIREBASE TOKEN GENERATOR (PEMBELI & PETANI)")
    print(f"{'='*60}")
    
    # Ambil credential dari .env
    email_pembeli = os.getenv("FIREBASE_EMAIL_PEMBELI", "buyer@example.com")
    email_petani = os.getenv("FIREBASE_EMAIL_PETANI", "farmer@example.com")
    
    # PROSES PEMBELI
    print(f"\n[1/4] Memastikan user Pembeli ada di Firebase...")
    user_pembeli = create_or_get_user(email_pembeli, "Pembeli Test")
    
    print(f"\n[2/4] Generating ID Token Pembeli via Custom Token...")
    token_pembeli, _ = get_id_token_via_custom_token(user_pembeli.uid)
    print_token_info("Pembeli", email_pembeli, user_pembeli.uid, token_pembeli)
    
    # PROSES PETANI
    print(f"\n[3/4] Memastikan user Petani ada di Firebase...")
    user_petani = create_or_get_user(email_petani, "Petani Test")
    
    print(f"\n[4/4] Generating ID Token Petani via Custom Token...")
    token_petani, _ = get_id_token_via_custom_token(user_petani.uid)
    print_token_info("Petani", email_petani, user_petani.uid, token_petani)

if __name__ == "__main__":
    main()
