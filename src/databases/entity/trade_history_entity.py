from sqlalchemy import Column, DateTime, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from ..database import engine, Base


class TradeHistoryEntity(Base):
    """TradeHistory"""

    __tablename__ = "trade_history"
    __table_args__ = {"schema": "kestrel"}

    id = Column(Integer, primary_key=True, autoincrement="auto")
    job_id = Column(String(255), unique=False, nullable=True)
    name = Column(String(255), unique=False, nullable=True)
    unit = Column(String(255), unique=False, nullable=True)
    decision = Column(String(255), unique=False, nullable=True)
    reason = Column(Text, nullable=True)
    trading_volume = Column(Float, nullable=True)
    trading_unit_price = Column(Float, nullable=True)
    trading_price = Column(Float, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_token_cost = Column(Float, nullable=True)
    exchange_provider = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<TradeHistory id={self.id}, name={self.name}, unit={self.unit}, decision={self.decision}>"


Base.metadata.create_all(engine)
