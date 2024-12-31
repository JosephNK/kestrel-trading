# from sqlalchemy import Column, DateTime, Integer, Float, String, Text
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql import func

# from ..database import engine, Base


# class TaskJobEntity(Base):
#     """TradeHistory"""

#     __tablename__ = "trade_history"

#     id = Column(Integer, primary_key=True, autoincrement="auto")
#     name = Column(String(255), unique=False, nullable=True)
#     user_id = Column(String(255), nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#     deleted_at = Column(DateTime(timezone=True))

#     def __repr__(self):
#         return f"<TradeHistory id={self.id}, name={self.name}, unit={self.unit}, decision={self.decision}>"


# Base.metadata.create_all(engine)
