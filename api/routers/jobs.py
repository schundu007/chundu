"""
Jobs router - CRUD operations for job listings
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Job, Company, JobApplication, ExcludedJob
from ..schemas.job import JobCreate, JobResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    company: Optional[str] = None,
    search: Optional[str] = None,
    min_score: Optional[float] = None,
    include_applied: bool = False,
    include_excluded: bool = False,
    db: Session = Depends(get_db)
):
    """List jobs with optional filters"""
    query = db.query(Job).filter(Job.is_active == True)

    # Apply filters
    if source:
        query = query.filter(Job.source == source)

    if company:
        query = query.join(Company).filter(Company.name.ilike(f"%{company}%"))

    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )

    if min_score is not None:
        query = query.filter(Job.match_score >= min_score)

    # Get user_id (default to 1 for single-user)
    user_id = 1

    # Exclude applied jobs unless requested
    if not include_applied:
        applied_ids = db.query(JobApplication.job_id).filter(
            JobApplication.user_id == user_id
        ).subquery()
        query = query.filter(~Job.id.in_(applied_ids))

    # Exclude excluded jobs unless requested
    if not include_excluded:
        excluded_ids = db.query(ExcludedJob.job_id).filter(
            ExcludedJob.user_id == user_id
        ).subquery()
        query = query.filter(~Job.id.in_(excluded_ids))

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    jobs = query.order_by(Job.match_score.desc().nullslast(), Job.posted_date.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()

    return JobListResponse(
        jobs=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a single job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobResponse)
def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Create or update a job listing"""
    # Check if job already exists
    existing = db.query(Job).filter(
        Job.external_id == job_data.external_id,
        Job.source == job_data.source
    ).first()

    if existing:
        # Update existing job
        for key, value in job_data.model_dump(exclude_unset=True).items():
            if key not in ["company_name", "company_logo"]:
                setattr(existing, key, value)
        existing.last_seen_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create company if needed
    company_id = None
    if job_data.company_name:
        company = db.query(Company).filter(
            Company.name == job_data.company_name
        ).first()
        if not company:
            company = Company(
                name=job_data.company_name,
                logo_url=job_data.company_logo
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        company_id = company.id

    # Create new job
    job = Job(
        external_id=job_data.external_id,
        company_id=company_id,
        title=job_data.title,
        location=job_data.location,
        department=job_data.department,
        description=job_data.description,
        salary=job_data.salary,
        work_type=job_data.work_type,
        url=job_data.url,
        posted_date=job_data.posted_date,
        source=job_data.source,
        match_score=job_data.match_score
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/batch", response_model=List[JobResponse])
def create_jobs_batch(jobs_data: List[JobCreate], db: Session = Depends(get_db)):
    """Create or update multiple jobs"""
    results = []
    for job_data in jobs_data:
        result = create_job(job_data, db)
        results.append(result)
    return results


@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Soft delete a job (mark as inactive)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_active = False
    db.commit()
    return {"message": "Job deleted"}
