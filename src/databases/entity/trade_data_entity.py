from sqlalchemy import Column, DateTime, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from ..database import engine, Base


class TradeDataEntity(Base):
    """TradeData"""

    __tablename__ = "trade_data"
    __table_args__ = {"schema": "kestrel"}

    id = Column(Integer, primary_key=True, autoincrement="auto")
    job_id = Column(String(255), unique=False, nullable=True)
    initial_investment = Column(Integer, nullable=True)  # 초기 투자금액
    trading_option = Column(String(255), nullable=True)  # BuyAndHold, Compounding
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<TradeData id={self.id}, job_id={self.job_id}, initial_investment={self.initial_investment}, trading_option={self.trading_option}>"


Base.metadata.create_all(engine)
