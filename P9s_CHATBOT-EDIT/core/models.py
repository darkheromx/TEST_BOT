#Path : core/models.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from services.database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role          = Column(String, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

class FAQ(Base):
    __tablename__ = "faq"
    id         = Column(Integer, primary_key=True, index=True)
    question   = Column(Text, nullable=False)
    answer     = Column(Text, nullable=False)
    category   = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(String)
    intent    = Column(String)
    question  = Column(Text)
    answer    = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class OOSLog(Base):
    __tablename__ = "oos_logs"
    id        = Column(Integer, primary_key=True, index=True)
    message   = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class PendingQuestion(Base):
    __tablename__ = "pending_questions"
    id             = Column(Integer, primary_key=True, index=True)
    user_platform  = Column(String, nullable=False)
    user_id        = Column(String, nullable=False)
    question       = Column(Text, nullable=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    is_answered    = Column(Boolean, default=False)
    answered_by    = Column(String)
    answered_at    = Column(DateTime(timezone=True))
    admin_answer   = Column(Text)

class Lead(Base):
    __tablename__ = "leads"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(String)
    name      = Column(String)
    phone     = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
