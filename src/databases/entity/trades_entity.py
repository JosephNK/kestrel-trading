from sqlalchemy import Column, DateTime, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from ..database import engine, Base


class Trades(Base):
    """Trades."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    decision = Column(String(255), unique=False, nullable=True)
    percentage = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    # btc_balance = Column(Float, nullable=True)
    # krw_balance = Column(Float, nullable=True)
    # btc_avg_buy_price = Column(Float, nullable=True)
    # btc_krw_price = Column(Float, nullable=True)
    currency = Column(String(255), nullable=True)
    provider = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Trades id={self.id}, decision={self.decision}, percentage={self.percentage}>"


Base.metadata.create_all(engine)
