from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_URI

# 데이터베이스 연결
engine = create_engine(
    DATABASE_URI,
    client_encoding="utf8",
    poolclass=NullPool,
    echo=True,
    # connect_args={
    #     "options": "-csearch_path={}".format("kestrel"),
    # },
)

# 스키마 생성 (없는 경우)
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS kestrel"))
    conn.commit()

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
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
