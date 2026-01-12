"""
Job and Company models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    board = Column(String(100))
    ats_type = Column(String(50))
    logo_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="company")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"))
    title = Column(String(500), nullable=False)
    location = Column(String(255))
    department = Column(String(255))
    description = Column(Text)
    salary = Column(String(255))
    work_type = Column(String(50))
    url = Column(String(1000))
    posted_date = Column(DateTime(timezone=True))
    source = Column(String(50), nullable=False)
    match_score = Column(Numeric(5, 2))
    is_active = Column(Boolean, default=True)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")
    exclusions = relationship("ExcludedJob", back_populates="job")
    documents = relationship("GeneratedDocument", back_populates="job")
