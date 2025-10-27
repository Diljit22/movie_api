"""
SQLAlchemy ORM models for the database tables.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from user_service.src.user_api.database import Base

class User(Base):
    """
    User model representing the 'users' table in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())