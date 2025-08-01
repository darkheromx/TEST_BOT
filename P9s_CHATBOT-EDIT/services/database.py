# services/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# สร้าง engine จาก DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # สำหรับ SQLite
)
# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base class สำหรับโมเดล
Base = declarative_base()

def get_db():
    """
    Dependency สำหรับ FastAPI:
    - yield session แล้วปิดเมื่อจบ request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
