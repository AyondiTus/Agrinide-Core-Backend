"""
Script untuk mendapatkan Firebase ID Token untuk testing.
Menggunakan Firebase Admin SDK Custom Token (tanpa password).

Jalankan dari root project:
    python tests/get_firebase_token.py
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
        return data.get("idToken")
    else:
        error_msg = data.get("error", {}).get("message", "Unknown error")
        print(f"  [FAIL] Token exchange gagal: {error_msg}")
        return None

def main():
    if not FIREBASE_API_KEY:
        print("[ERROR] FIREBASE_API_KEY belum diset di .env!")
        return
    
    print(f"{'='*60}")
    print(f"  FIREBASE TOKEN GENERATOR")
    print(f"{'='*60}")
    
    email = os.getenv("FIREBASE_EMAIL", "test@example.com")
    
    print(f"\n[1/2] Memastikan user ada di Firebase...")
    user = create_or_get_user(email)
    
    print(f"\n[2/2] Generating ID Token via Custom Token...")
    token = get_id_token_via_custom_token(user.uid)
    
    if token:
        print(f"\n{'='*60}")
        print(f"  TOKEN BERHASIL DIDAPATKAN!")
        print(f"{'='*60}")
        print(f"\n  UID   : {user.uid}")
        print(f"  Email : {email}")
        print(f"\n  ID Token (copy ke Bruno/Postman):")
        print(f"  {'-'*55}")
        print(f"  {token}")
        print(f"  {'-'*55}")
        print(f"\n  Token berlaku selama 1 jam.")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
