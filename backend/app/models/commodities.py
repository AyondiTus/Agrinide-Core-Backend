import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    price_per_kg = Column(Numeric(12, 2), nullable=False)
    current_stock = Column(Numeric(10, 2), nullable=False)
    location = Column(String(255))
    path_image = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    farmer = relationship("User", back_populates="commodities")
    negotiations = relationship("Negotiation", back_populates="commodity", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="commodity", cascade="all, delete-orphan")
