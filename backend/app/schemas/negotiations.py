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

# --- Request Schemas ---

class NegotiationStart(BaseModel):
    commodity_id: UUID
    price: float = Field(..., gt=0)
    volume: float = Field(..., gt=0)
    quality_grade_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    payment_term_id: Optional[int] = None
    shipping_point_id: Optional[int] = None
    delivery_type_id: Optional[int] = None

class NegotiationCounter(BaseModel):
    price: Optional[float] = Field(None, gt=0)
    volume: Optional[float] = Field(None, gt=0)
    quality_grade_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    payment_term_id: Optional[int] = None
    shipping_point_id: Optional[int] = None
    delivery_type_id: Optional[int] = None

# --- Response Schemas ---

class NegotiationHistoryResponse(BaseModel):
    id: UUID
    price: float
    volume: float
    quality_grade_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    payment_term_id: Optional[int] = None
    shipping_point_id: Optional[int] = None
    delivery_type_id: Optional[int] = None
    proposed_by: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class NegotiationResponse(BaseModel):
    id: UUID
    farmer_id: str
    buyer_id: str
    commodity_id: UUID
    current_price: float
    current_volume: float
    quality_grade_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    payment_term_id: Optional[int] = None
    shipping_point_id: Optional[int] = None
    delivery_type_id: Optional[int] = None
    proposed_by: str
    status: str
    updated_at: Optional[datetime] = None

    farmer: Optional[FarmerBuyerInfo] = None
    buyer: Optional[FarmerBuyerInfo] = None
    commodity: Optional[CommodityInfo] = None

    model_config = ConfigDict(from_attributes=True)

class NegotiationDetailResponse(NegotiationResponse):
    histories: List[NegotiationHistoryResponse] = []
