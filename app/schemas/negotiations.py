from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# --- Nested Info Schemas ---

class FarmerBuyerInfo(BaseModel):
    id: str
    name: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class CommodityInfo(BaseModel):
    id: UUID
    name: str
    price_per_kg: float
    location: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TemplateInfo(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# --- Request Schemas ---

class NegotiationStart(BaseModel):
    commodity_id: UUID
    template_id: UUID
    price: float = Field(..., gt=0, description="Harga penawaran awal harus > 0")
    volume: float = Field(..., gt=0, description="Volume penawaran awal harus > 0")
    quality_grade: Optional[str] = None
    payment_method: Optional[str] = None
    payment_term: Optional[str] = None
    shipping_point: Optional[str] = None
    delivery_type: Optional[str] = None

class NegotiationCounter(BaseModel):
    price: Optional[float] = Field(None, gt=0)
    volume: Optional[float] = Field(None, gt=0)
    quality_grade: Optional[str] = None
    payment_method: Optional[str] = None
    payment_term: Optional[str] = None
    shipping_point: Optional[str] = None
    delivery_type: Optional[str] = None

# --- Response Schemas ---

class NegotiationHistoryResponse(BaseModel):
    id: UUID
    price: float
    volume: float
    quality_grade: Optional[str] = None
    payment_method: Optional[str] = None
    payment_term: Optional[str] = None
    shipping_point: Optional[str] = None
    delivery_type: Optional[str] = None
    proposed_by: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NegotiationResponse(BaseModel):
    id: UUID
    template_id: UUID
    farmer_id: str
    buyer_id: str
    commodity_id: UUID
    current_price: float
    current_volume: float
    quality_grade: Optional[str] = None
    payment_method: Optional[str] = None
    payment_term: Optional[str] = None
    shipping_point: Optional[str] = None
    delivery_type: Optional[str] = None
    proposed_by: str
    status: str
    updated_at: Optional[datetime] = None

    farmer: Optional[FarmerBuyerInfo] = None
    buyer: Optional[FarmerBuyerInfo] = None
    commodity: Optional[CommodityInfo] = None
    template: Optional[TemplateInfo] = None

    model_config = ConfigDict(from_attributes=True)

class NegotiationDetailResponse(NegotiationResponse):
    histories: List[NegotiationHistoryResponse] = []
