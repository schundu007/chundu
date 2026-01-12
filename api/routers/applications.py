"""
Applications router - Track job applications
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import Job, Company, JobApplication
from ..schemas.application import (
    ApplicationCreate, ApplicationResponse, ApplicationListResponse
)

router = APIRouter(prefix="/applications", tags=["applications"])

# Default user ID for single-user mode
DEFAULT_USER_ID = 1


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all job applications"""
    query = db.query(JobApplication)\
        .options(joinedload(JobApplication.job).joinedload(Job.company))\
        .filter(JobApplication.user_id == DEFAULT_USER_ID)

    if status:
        query = query.filter(JobApplication.status == status)

    applications = query.order_by(JobApplication.applied_at.desc()).all()

    return ApplicationListResponse(
        applications=[ApplicationResponse.model_validate(app) for app in applications],
        total=len(applications)
    )


@router.post("", response_model=ApplicationResponse)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Mark a job as applied"""
    # Check if job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()

    # If job doesn't exist and job_data provided, create it
    if not job and data.job_data:
        company_id = None
        if data.job_data.get("company"):
            company = db.query(Company).filter(
                Company.name == data.job_data["company"]
            ).first()
            if not company:
                company = Company(
                    name=data.job_data["company"],
                    logo_url=data.job_data.get("companyLogo")
                )
                db.add(company)
                db.commit()
                db.refresh(company)
            company_id = company.id

        job = Job(
            external_id=data.job_data.get("id", str(data.job_id)),
            company_id=company_id,
            title=data.job_data.get("title", "Unknown"),
            location=data.job_data.get("location"),
            department=data.job_data.get("department"),
            url=data.job_data.get("url"),
            source=data.job_data.get("source", "manual")
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        data.job_id = job.id

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == DEFAULT_USER_ID,
        JobApplication.job_id == data.job_id
    ).first()

    if existing:
        # Update existing application
        existing.status = data.status
        if data.notes:
            existing.notes = data.notes
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    # Create new application
    application = JobApplication(
        user_id=DEFAULT_USER_ID,
        job_id=data.job_id,
        status=data.status,
        notes=data.notes
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    # Load job relationship
    db.refresh(application)
    return application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    status: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update application status"""
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == DEFAULT_USER_ID
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = status
    if notes is not None:
        application.notes = notes
    application.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db)):
    """Remove an application record"""
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == DEFAULT_USER_ID
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()
    return {"message": "Application deleted"}


# Excluded jobs endpoints
from ..models import ExcludedJob
from ..schemas.application import ExcludedJobCreate, ExcludedJobResponse


@router.get("/excluded", response_model=List[ExcludedJobResponse])
def list_excluded(db: Session = Depends(get_db)):
    """List all excluded jobs"""
    excluded = db.query(ExcludedJob)\
        .options(joinedload(ExcludedJob.job).joinedload(Job.company))\
        .filter(ExcludedJob.user_id == DEFAULT_USER_ID)\
        .order_by(ExcludedJob.excluded_at.desc())\
        .all()

    return [ExcludedJobResponse.model_validate(e) for e in excluded]


@router.post("/excluded", response_model=ExcludedJobResponse)
def exclude_job(data: ExcludedJobCreate, db: Session = Depends(get_db)):
    """Exclude a job from listings"""
    # Check if job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()

    # If job doesn't exist and job_data provided, create it
    if not job and data.job_data:
        company_id = None
        if data.job_data.get("company"):
            company = db.query(Company).filter(
                Company.name == data.job_data["company"]
            ).first()
            if not company:
                company = Company(
                    name=data.job_data["company"],
                    logo_url=data.job_data.get("companyLogo")
                )
                db.add(company)
                db.commit()
                db.refresh(company)
            company_id = company.id

        job = Job(
            external_id=data.job_data.get("id", str(data.job_id)),
            company_id=company_id,
            title=data.job_data.get("title", "Unknown"),
            location=data.job_data.get("location"),
            department=data.job_data.get("department"),
            url=data.job_data.get("url"),
            source=data.job_data.get("source", "manual")
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        data.job_id = job.id

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if already excluded
    existing = db.query(ExcludedJob).filter(
        ExcludedJob.user_id == DEFAULT_USER_ID,
        ExcludedJob.job_id == data.job_id
    ).first()

    if existing:
        return existing

    # Create exclusion
    excluded = ExcludedJob(
        user_id=DEFAULT_USER_ID,
        job_id=data.job_id,
        reason=data.reason
    )
    db.add(excluded)
    db.commit()
    db.refresh(excluded)
    return excluded


@router.delete("/excluded/{excluded_id}")
def restore_job(excluded_id: int, db: Session = Depends(get_db)):
    """Remove exclusion (restore job to listings)"""
    excluded = db.query(ExcludedJob).filter(
        ExcludedJob.id == excluded_id,
        ExcludedJob.user_id == DEFAULT_USER_ID
    ).first()

    if not excluded:
        raise HTTPException(status_code=404, detail="Exclusion not found")

    db.delete(excluded)
    db.commit()
    return {"message": "Job restored"}
