from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Provinsi(Base):
    __tablename__ = "provinsi"

    id = Column(Integer, primary_key=True, index=True)
    provinsi_name = Column(String(50), nullable=False)

    kota = relationship("Kota", back_populates="provinsi", cascade="all, delete-orphan")


class Kota(Base):
    __tablename__ = "kota"

    id = Column(Integer, primary_key=True, index=True)
    provinsi_id = Column(Integer, ForeignKey("provinsi.id", ondelete="CASCADE"), nullable=False)
    kota_name = Column(String(50), nullable=False)

    provinsi = relationship("Provinsi", back_populates="kota")
    kecamatan = relationship("Kecamatan", back_populates="kota", cascade="all, delete-orphan")


class Kecamatan(Base):
    __tablename__ = "kecamatan"

    id = Column(Integer, primary_key=True, index=True)
    kota_id = Column(Integer, ForeignKey("kota.id", ondelete="CASCADE"), nullable=False)
    kecamatan_name = Column(String(50), nullable=False)

    kota = relationship("Kota", back_populates="kecamatan")
