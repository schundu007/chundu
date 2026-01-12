"""
Job Search API - FastAPI Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .routers import jobs_router, applications_router, documents_router, settings_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


app = FastAPI(
    title="Job Search API",
    description="Backend API for job search, tracking, and document generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(settings_router, prefix="/api")


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Job Search API is running"}


@app.get("/api/health")
def health():
    """Health check for API"""
    return {"status": "healthy"}


# Migration endpoint for importing localStorage data
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Job, Company, JobApplication, ExcludedJob
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class LocalStorageImport(BaseModel):
    applied_jobs: List[str] = []
    applied_jobs_data: Dict[str, dict] = {}
    excluded_jobs: List[str] = []


@app.post("/api/migration/import")
def import_localstorage(data: LocalStorageImport, db: Session = Depends(get_db)):
    """Import data from localStorage"""
    imported = {"applications": 0, "excluded": 0, "jobs_created": 0}
    user_id = 1

    # Process applied jobs
    for job_id in data.applied_jobs:
        job_data = data.applied_jobs_data.get(job_id, {})

        # Find or create company
        company_id = None
        if job_data.get("company"):
            company = db.query(Company).filter(
                Company.name == job_data["company"]
            ).first()
            if not company:
                company = Company(
                    name=job_data["company"],
                    logo_url=job_data.get("companyLogo")
                )
                db.add(company)
                db.commit()
                db.refresh(company)
            company_id = company.id

        # Find or create job
        job = db.query(Job).filter(
            Job.external_id == job_id
        ).first()

        if not job:
            job = Job(
                external_id=job_id,
                company_id=company_id,
                title=job_data.get("title", "Unknown"),
                location=job_data.get("location"),
                department=job_data.get("department"),
                url=job_data.get("url"),
                source="imported"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            imported["jobs_created"] += 1

        # Create application if not exists
        existing = db.query(JobApplication).filter(
            JobApplication.user_id == user_id,
            JobApplication.job_id == job.id
        ).first()

        if not existing:
            applied_at = datetime.utcnow()
            if job_data.get("appliedAt"):
                try:
                    applied_at = datetime.fromisoformat(job_data["appliedAt"].replace("Z", "+00:00"))
                except:
                    pass

            application = JobApplication(
                user_id=user_id,
                job_id=job.id,
                applied_at=applied_at
            )
            db.add(application)
            imported["applications"] += 1

    # Process excluded jobs
    for job_id in data.excluded_jobs:
        # Find or create job
        job = db.query(Job).filter(
            Job.external_id == job_id
        ).first()

        if not job:
            job = Job(
                external_id=job_id,
                title="Unknown",
                source="imported"
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            imported["jobs_created"] += 1

        # Create exclusion if not exists
        existing = db.query(ExcludedJob).filter(
            ExcludedJob.user_id == user_id,
            ExcludedJob.job_id == job.id
        ).first()

        if not existing:
            exclusion = ExcludedJob(
                user_id=user_id,
                job_id=job.id
            )
            db.add(exclusion)
            imported["excluded"] += 1

    db.commit()
    return {
        "message": "Import complete",
        "imported": imported
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
