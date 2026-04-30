from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(128), primary_key=True, index=True, comment="Firebase UID")
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    role = Column(String(50), nullable=False, comment="farmer atau buyer")
    address_city = Column(String(100))
    address_province = Column(String(100))
    address_detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships will be added here
    commodities = relationship("Commodity", back_populates="farmer", cascade="all, delete-orphan")
    negotiations_proposed = relationship("Negotiation", foreign_keys="[Negotiation.proposed_by]", back_populates="proposer")
    negotiations_as_farmer = relationship("Negotiation", foreign_keys="[Negotiation.farmer_id]", back_populates="farmer")
    negotiations_as_buyer = relationship("Negotiation", foreign_keys="[Negotiation.buyer_id]", back_populates="buyer")
    contracts_as_farmer = relationship("Contract", foreign_keys="[Contract.farmer_id]", back_populates="farmer")
    contracts_as_buyer = relationship("Contract", foreign_keys="[Contract.buyer_id]", back_populates="buyer")
    negotiation_histories = relationship("NegotiationHistory", back_populates="proposer")
