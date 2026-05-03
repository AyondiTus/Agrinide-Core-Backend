from sqlalchemy import Column, Integer, String
from app.models.base import Base


class QualityGrade(Base):
    __tablename__ = "quality_grade"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(100), nullable=False, comment="Contoh: Grade A Premium")


class PaymentMethod(Base):
    __tablename__ = "payment_method"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(100), nullable=False)


class PaymentTerm(Base):
    __tablename__ = "payment_term"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(100), nullable=False, comment="Contoh: DP 30%, CBD, Termin 14 Hari")


class ShippingPoint(Base):
    __tablename__ = "shipping_point"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(100), nullable=False, comment="Contoh: Loco Gudang Petani, Franko Pabrik")


class DeliveryType(Base):
    __tablename__ = "delivery_type"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(100), nullable=False, comment="Contoh: Sekaligus (Full), Bertahap (Parsial)")
