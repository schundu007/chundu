"""
Job and Company Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CompanyBase(BaseModel):
    name: str
    board: Optional[str] = None
    ats_type: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    external_id: str
    title: str
    location: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    work_type: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[datetime] = None
    source: str
    match_score: Optional[float] = None


class JobCreate(JobBase):
    company_name: Optional[str] = None
    company_logo: Optional[str] = None


class JobResponse(JobBase):
    id: int
    company_id: Optional[int] = None
    company: Optional[CompanyResponse] = None
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    is_applied: Optional[bool] = False
    is_excluded: Optional[bool] = False

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
