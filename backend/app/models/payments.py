import uuid
from sqlalchemy import Column, String, Numeric, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    contract_hash_id = Column(String(64), ForeignKey("contracts.hash_id", ondelete="RESTRICT"), nullable=False)
    payer_id = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, comment="User (Buyer) yang melakukan pembayaran")

    amount = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(String(50), nullable=False, comment="Contoh: DP, Termin 1, Pelunasan")

    # Konfirmasi Manual
    payment_receipt_url = Column(Text, comment="URL gambar bukti transfer dari Firebase Storage")
    sender_bank = Column(String(100), comment="Bank asal pembeli, misal: BCA, Mandiri")
    sender_name = Column(String(255), comment="Nama pemilik rekening pengirim")

    status = Column(String(50), server_default="pending", comment="pending, awaiting_verification, verified, rejected")
    rejection_reason = Column(Text, comment="Alasan penolakan jika bukti transfer tidak valid")

    verified_by = Column(String(128), ForeignKey("users.id", ondelete="RESTRICT"), nullable=True, comment="User (Petani) yang melakukan verifikasi")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Waktu pembayaran disahkan oleh Petani")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    contract = relationship("Contract", back_populates="payments")
    payer = relationship("User", foreign_keys=[payer_id], back_populates="payments_made")
    verifier = relationship("User", foreign_keys=[verified_by], back_populates="payments_verified")
