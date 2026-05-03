from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    id_provinsi: Optional[int] = None
    id_kota: Optional[int] = None
    id_kecamatan: Optional[int] = None
    address_detail: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    id_provinsi: Optional[int] = None
    id_kota: Optional[int] = None
    id_kecamatan: Optional[int] = None
    address_detail: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
