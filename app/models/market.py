import uuid
from sqlalchemy import Column, String, Integer, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(String(100), primary_key=True, comment="Contoh: cabe_rawit_merah")
    name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=False)

    daily_prices = relationship("MarketPriceDaily", back_populates="market_price", cascade="all, delete-orphan")


class MarketPriceDaily(Base):
    __tablename__ = "market_price_daily"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    market_price_id = Column(String(100), ForeignKey("market_prices.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    current_price = Column(Integer, nullable=False)
    previous_price = Column(Integer, nullable=False)
    change_rp = Column(Integer, nullable=False)
    change_percentage = Column(Numeric(5, 2), nullable=False)
    trend = Column(String(20), comment="up, down, stable")

    market_price = relationship("MarketPrice", back_populates="daily_prices")
