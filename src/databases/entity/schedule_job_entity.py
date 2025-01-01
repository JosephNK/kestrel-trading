from sqlalchemy import Column, DateTime, Integer, Float, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from ..database import engine, Base


class ScheduleJobEntity(Base):
    """ScheduleJob"""

    __tablename__ = "schedule_job"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    job_id = Column(String(255), unique=True, nullable=True)
    user_id = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return (
            f"<ScheduleJob id={self.id}, job_id={self.job_id}, user_id={self.user_id}>"
        )


Base.metadata.create_all(engine)
