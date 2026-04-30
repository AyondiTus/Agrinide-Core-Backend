import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("contract_templates.id", ondelete="RESTRICT"), nullable=False)
    farmer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    buyer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)
    current_volume = Column(Numeric(10, 2), nullable=False)
    
    quality_grade = Column(String(100), comment="Contoh: Grade A Premium")
    payment_method = Column(String(100), comment="Contoh: Transfer Bank, Escrow")
    payment_term = Column(String(100), comment="Contoh: DP 30%, CBD, Termin 14 Hari")
    shipping_point = Column(String(255), comment="Contoh: Loco Gudang Petani, Franko Pabrik")
    delivery_type = Column(String(100), comment="Contoh: Sekaligus (Full), Bertahap (Parsial)")
    
    proposed_by = Column(String(128), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), server_default='negotiating', comment="negotiating, accepted, rejected")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    template = relationship("ContractTemplate", back_populates="negotiations")
    farmer = relationship("User", foreign_keys=[farmer_id], back_populates="negotiations_as_farmer")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="negotiations_as_buyer")
    commodity = relationship("Commodity", back_populates="negotiations")
    proposer = relationship("User", foreign_keys=[proposed_by], back_populates="negotiations_proposed")
    histories = relationship("NegotiationHistory", back_populates="negotiation", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="negotiation", uselist=False)


class NegotiationHistory(Base):
    __tablename__ = "negotiation_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    volume = Column(Numeric(10, 2), nullable=False)
    
    quality_grade = Column(String(100))
    payment_method = Column(String(100))
    payment_term = Column(String(100))
    shipping_point = Column(String(255))
    delivery_type = Column(String(100))
    
    proposed_by = Column(String(128), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    negotiation = relationship("Negotiation", back_populates="histories")
    proposer = relationship("User", back_populates="negotiation_histories")
