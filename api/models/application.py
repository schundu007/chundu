"""
Application, Exclusion, Document, and Settings models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    status = Column(String(50), default="applied")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    job = relationship("Job", back_populates="applications")


class ExcludedJob(Base):
    __tablename__ = "excluded_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    excluded_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(255))

    job = relationship("Job", back_populates="exclusions")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"))
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    document_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    ai_model = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="documents")


class UserSetting(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"))
    setting_key = Column(String(100), nullable=False)
    setting_value = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
