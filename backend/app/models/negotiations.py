import uuid
from sqlalchemy import Column, String, Numeric, DateTime, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Negotiation(Base):
    __tablename__ = "negotiations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    farmer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    buyer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="RESTRICT"), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)
    current_volume = Column(Numeric(10, 2), nullable=False)

    quality_grade_id = Column(Integer, ForeignKey("quality_grade.id"), nullable=True)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=True)
    payment_term_id = Column(Integer, ForeignKey("payment_term.id"), nullable=True)
    shipping_point_id = Column(Integer, ForeignKey("shipping_point.id"), nullable=True)
    delivery_type_id = Column(Integer, ForeignKey("delivery_type.id"), nullable=True)

    proposed_by = Column(String(128), ForeignKey("users.id"), nullable=False)
    status = Column(String(50), server_default='negotiating', comment="negotiating, accepted, rejected")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    farmer = relationship("User", foreign_keys=[farmer_id], back_populates="negotiations_as_farmer")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="negotiations_as_buyer")
    commodity = relationship("Commodity", back_populates="negotiations")
    proposer = relationship("User", foreign_keys=[proposed_by], back_populates="negotiations_proposed")
    histories = relationship("NegotiationHistory", back_populates="negotiation", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="negotiation", uselist=False)

    quality_grade = relationship("QualityGrade", foreign_keys=[quality_grade_id])
    payment_method = relationship("PaymentMethod", foreign_keys=[payment_method_id])
    payment_term = relationship("PaymentTerm", foreign_keys=[payment_term_id])
    shipping_point = relationship("ShippingPoint", foreign_keys=[shipping_point_id])
    delivery_type = relationship("DeliveryType", foreign_keys=[delivery_type_id])


class NegotiationHistory(Base):
    __tablename__ = "negotiation_histories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    volume = Column(Numeric(10, 2), nullable=False)

    quality_grade_id = Column(Integer, ForeignKey("quality_grade.id"), nullable=True)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=True)
    payment_term_id = Column(Integer, ForeignKey("payment_term.id"), nullable=True)
    shipping_point_id = Column(Integer, ForeignKey("shipping_point.id"), nullable=True)
    delivery_type_id = Column(Integer, ForeignKey("delivery_type.id"), nullable=True)

    proposed_by = Column(String(128), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    negotiation = relationship("Negotiation", back_populates="histories")
    proposer = relationship("User", back_populates="negotiation_histories")

    quality_grade = relationship("QualityGrade", foreign_keys=[quality_grade_id])
    payment_method = relationship("PaymentMethod", foreign_keys=[payment_method_id])
    payment_term = relationship("PaymentTerm", foreign_keys=[payment_term_id])
    shipping_point = relationship("ShippingPoint", foreign_keys=[shipping_point_id])
    delivery_type = relationship("DeliveryType", foreign_keys=[delivery_type_id])
