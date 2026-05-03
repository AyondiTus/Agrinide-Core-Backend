from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class FarmerInfo(BaseModel):
    id: str
    name: str
    id_provinsi: Optional[int] = None
    id_kota: Optional[int] = None
    id_kecamatan: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class CommodityBase(BaseModel):
    name: str
    price_per_kg: float = Field(..., gt=0, description="Harga harus lebih besar dari 0")
    current_stock: float = Field(..., ge=0, description="Stok tidak boleh negatif")
    location: Optional[str] = None
    path_image: Optional[str] = None
    is_active: bool = True

class CommodityCreate(CommodityBase):
    pass

class CommodityUpdate(BaseModel):
    name: Optional[str] = None
    price_per_kg: Optional[float] = Field(None, gt=0)
    current_stock: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    path_image: Optional[str] = None
    is_active: Optional[bool] = None

class CommodityResponse(CommodityBase):
    id: UUID
    farmer_id: str
    updated_at: Optional[datetime] = None
    farmer: Optional[FarmerInfo] = None

    model_config = ConfigDict(from_attributes=True)

class BulkInsertFeedback(BaseModel):
    row_number: int
    error_message: str

class BulkInsertResponse(BaseModel):
    success: bool
    inserted_count: int = 0
    errors: List[BulkInsertFeedback] = []
