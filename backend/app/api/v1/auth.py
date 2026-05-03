from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.users import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter()

@router.post("/register/petani", response_model=UserResponse)
async def register_petani(
    user_data: UserCreate | None = None,
    db: AsyncSession = Depends(get_db),
    decoded_token: dict = Depends(get_current_user)
):
    return await auth_service.register_user(db, decoded_token, "farmer", user_data)

@router.post("/register/pembeli", response_model=UserResponse)
async def register_pembeli(
    user_data: UserCreate | None = None,
    db: AsyncSession = Depends(get_db),
    decoded_token: dict = Depends(get_current_user)
):
    return await auth_service.register_user(db, decoded_token, "buyer", user_data)

@router.post("/login", response_model=UserResponse)
async def login(
    db: AsyncSession = Depends(get_db),
    decoded_token: dict = Depends(get_current_user)
):
    return await auth_service.login_user(db, decoded_token)

