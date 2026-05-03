from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Sawah(Base):
    __tablename__ = "sawah"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(String(128), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    id_provinsi = Column(Integer, ForeignKey("provinsi.id"), nullable=False)
    id_kota = Column(Integer, ForeignKey("kota.id"), nullable=False)
    id_kecamatan = Column(Integer, ForeignKey("kecamatan.id"), nullable=False)
    luas_sawah = Column(Numeric(10, 2))
    address_detail = Column(Text, nullable=True)
    kondisi_tanah = Column(String(50))
    description = Column(Text)

    # Relationships
    petani = relationship("User", back_populates="sawah")
    provinsi = relationship("Provinsi")
    kota = relationship("Kota")
    kecamatan = relationship("Kecamatan")
