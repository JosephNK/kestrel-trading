from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_URI

engine = create_engine(DATABASE_URI, echo=False)

# Create database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        print("Database Close")
        db.close()


@contextmanager
def get_scheduler_db():
    """스케줄러 전용 DB 세션 관리자"""
    db = SessionLocal()
    try:
        yield db
    finally:
        print("Database Close")
        db.close()
