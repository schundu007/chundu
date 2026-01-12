"""
Application, Exclusion, and Document Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .job import JobResponse


class ApplicationBase(BaseModel):
    status: str = "applied"
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    job_id: int
    # For creating job if it doesn't exist
    job_data: Optional[dict] = None


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    job_id: int
    applied_at: datetime
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    applications: List[ApplicationResponse]
    total: int


class ExcludedJobCreate(BaseModel):
    job_id: int
    reason: Optional[str] = None
    # For creating job if it doesn't exist
    job_data: Optional[dict] = None


class ExcludedJobResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    excluded_at: datetime
    reason: Optional[str] = None
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    job_id: int
    document_type: str  # 'cover_letter' or 'resume'
    # Optional: provide job data if job doesn't exist yet
    job_data: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    job_id: int
    document_type: str
    content: str
    ai_model: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
