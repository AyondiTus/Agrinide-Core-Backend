from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(128), primary_key=True, index=True, comment="Firebase UID")
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    role = Column(String(50), nullable=False, comment="farmer atau buyer")
    id_provinsi = Column(Integer, ForeignKey("provinsi.id"))
    id_kota = Column(Integer, ForeignKey("kota.id"))
    id_kecamatan = Column(Integer, ForeignKey("kecamatan.id"))
    address_detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships will be added here
    provinsi = relationship("Provinsi")
    kota = relationship("Kota")
    kecamatan = relationship("Kecamatan")
    sawah = relationship("Sawah", back_populates="petani", cascade="all, delete-orphan")
    
    commodities = relationship("Commodity", back_populates="farmer", cascade="all, delete-orphan")
    negotiations_proposed = relationship("Negotiation", foreign_keys="[Negotiation.proposed_by]", back_populates="proposer")
    negotiations_as_farmer = relationship("Negotiation", foreign_keys="[Negotiation.farmer_id]", back_populates="farmer")
    negotiations_as_buyer = relationship("Negotiation", foreign_keys="[Negotiation.buyer_id]", back_populates="buyer")
    contracts_as_farmer = relationship("Contract", foreign_keys="[Contract.farmer_id]", back_populates="farmer")
    contracts_as_buyer = relationship("Contract", foreign_keys="[Contract.buyer_id]", back_populates="buyer")
    negotiation_histories = relationship("NegotiationHistory", back_populates="proposer")
    payments_made = relationship("Payment", foreign_keys="[Payment.payer_id]", back_populates="payer")
    payments_verified = relationship("Payment", foreign_keys="[Payment.verified_by]", back_populates="verifier")
