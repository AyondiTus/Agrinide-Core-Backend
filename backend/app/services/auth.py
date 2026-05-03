from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from typing import Any

from app.schemas.users import UserCreate
from app.repositories import users as user_repo

def validate_token_data(decoded_token: dict) -> tuple[str, str]:
    uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    
    if not uid or not email:
        raise HTTPException(status_code=400, detail="Token must contain uid and email")
    
    return uid, email

async def get_existing_user(db: AsyncSession, uid: str) -> Any | None:
    return await user_repo.get_user_by_id(db, uid)

async def create_new_user(
    db: AsyncSession,
    uid: str,
    email: str,
    role: str,
    decoded_token: dict,
    user_data: UserCreate | None = None
) -> Any:
    if not user_data:
        user_data = UserCreate()
        
    name = user_data.name or decoded_token.get("name") or email.split("@")[0]
    
    return await user_repo.create_user(
        db=db,
        user_id=uid,
        email=email,
        name=name,
        role=role,
        phone=user_data.phone,
        id_provinsi=user_data.id_provinsi,
        id_kota=user_data.id_kota,
        id_kecamatan=user_data.id_kecamatan,
        address_detail=user_data.address_detail
    )

async def register_user(
    db: AsyncSession,
    decoded_token: dict,
    role: str,
    user_data: UserCreate | None = None
) -> Any:
    uid, email = validate_token_data(decoded_token)
    
    existing_user = await get_existing_user(db, uid)
    if existing_user:
        return existing_user
        
    return await create_new_user(db, uid, email, role, decoded_token, user_data)

async def login_user(db: AsyncSession, decoded_token: dict) -> Any:
    uid = decoded_token.get("uid")
    user = await user_repo.get_user_by_id(db, uid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User authenticated in Firebase but not found in Database. Please register first."
        )
    return user
