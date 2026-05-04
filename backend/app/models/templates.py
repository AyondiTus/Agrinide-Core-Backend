import uuid
from sqlalchemy import Column, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base

class ContractTemplate(Base):
    __tablename__ = "contract_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, comment="Contoh: Forward Contract, Spot Contract")
    description = Column(Text)
    base_text_prompt = Column(Text, nullable=False, comment="Instruksi dasar legal untuk Gemini AI")
    required_fields = Column(JSONB, comment="Definisi input form dinamis di frontend")

    # Relationships
    contracts = relationship("Contract", back_populates="template")
