import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Contract(Base):
    __tablename__ = "contracts"

    hash_id = Column(String(64), primary_key=True, comment="SHA-256 Hash Utama")
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"), unique=True, nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("contract_templates.id", ondelete="RESTRICT"), nullable=False)
    farmer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    buyer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False)
    
    total_volume = Column(Numeric(10, 2), nullable=False)
    remaining_volume = Column(Numeric(10, 2), nullable=False)
    price_agreed = Column(Numeric(12, 2), nullable=False)
    
    quality_grade = Column(String(100), nullable=False)
    payment_method = Column(String(100), nullable=False)
    payment_term = Column(String(100), nullable=False)
    shipping_point = Column(String(255), nullable=False)
    delivery_type = Column(String(100), nullable=False)
    
    status = Column(String(50), server_default='pending', comment="pending, partially_fulfilled, completed")
    mou_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    negotiation = relationship("Negotiation", back_populates="contract")
    template = relationship("ContractTemplate", back_populates="contracts")
    farmer = relationship("User", foreign_keys=[farmer_id], back_populates="contracts_as_farmer")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="contracts_as_buyer")
    commodity = relationship("Commodity", back_populates="contracts")
    fulfillments = relationship("Fulfillment", back_populates="contract")
    payments = relationship("Payment", back_populates="contract")


class Fulfillment(Base):
    __tablename__ = "fulfillments"

    hash_id = Column(String(64), primary_key=True, comment="SHA-256 Hash Pengiriman")
    contract_hash_id = Column(String(64), ForeignKey("contracts.hash_id", ondelete="RESTRICT"), nullable=False)
    delivery_volume = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), server_default='in_transit', comment="in_transit, received, rejected")
    buyer_notes = Column(Text)
    delivery_date = Column(DateTime(timezone=True), server_default=func.now())
    received_at = Column(DateTime(timezone=True))

    # Relationships
    contract = relationship("Contract", back_populates="fulfillments")
