"""
User profile model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    linkedin = Column(String(255))
    github = Column(String(255))
    website = Column(String(255))
    location = Column(String(255))
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
