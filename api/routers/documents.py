"""
Documents router - Generate and manage cover letters and resumes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List

from ..database import get_db
from ..models import Job, GeneratedDocument, UserSetting
from ..schemas.application import DocumentCreate, DocumentResponse
from ..config import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])

# Default user ID for single-user mode
DEFAULT_USER_ID = 1

# User profile for document generation
USER_PROFILE = {
    "name": "Sudhakar Chundu",
    "title": "Cloud AI Architect",
    "email": "chundubabu@gmail.com",
    "phone": "",
    "linkedin": "https://www.linkedin.com/in/schundu",
    "github": "https://github.com/schundu007",
    "website": "https://www.sudhakarchundu.org",
    "location": "United States",
    "years_experience": "18+",
    "summary": """Cloud AI Architect with 18+ years of experience in enterprise infrastructure,
    AI/ML platforms, and DevOps transformation. Expert in Kubernetes, GPU infrastructure,
    and building scalable cloud-native platforms.""",
    "skills": [
        "Cloud Architecture (AWS, Azure, GCP)",
        "Kubernetes & Container Orchestration",
        "GPU Infrastructure & AI/ML Platforms",
        "Terraform & Infrastructure as Code",
        "GitOps (ArgoCD, Flux)",
        "Prometheus, Grafana, Datadog",
        "Site Reliability Engineering",
        "Platform Engineering",
        "DevSecOps & Compliance (SOC2, HIPAA)",
        "Team Leadership & Mentoring",
        "Python, Go, Shell Scripting",
        "CI/CD (GitHub Actions, Jenkins, GitLab)"
    ]
}


def get_ai_client(db: Session):
    """Get AI client based on user settings"""
    settings = get_settings()

    # Check user settings for API key
    user_key = db.query(UserSetting).filter(
        UserSetting.user_id == DEFAULT_USER_ID,
        UserSetting.setting_key == "anthropic_api_key"
    ).first()

    api_key = user_key.setting_value if user_key else settings.anthropic_api_key

    if api_key:
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=api_key), "anthropic"
        except ImportError:
            pass

    # Fall back to OpenAI
    user_key = db.query(UserSetting).filter(
        UserSetting.user_id == DEFAULT_USER_ID,
        UserSetting.setting_key == "openai_api_key"
    ).first()

    api_key = user_key.setting_value if user_key else settings.openai_api_key

    if api_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=api_key), "openai"
        except ImportError:
            pass

    return None, None


def generate_cover_letter_content(job: Job, client, provider: str) -> str:
    """Generate cover letter using AI"""
    prompt = f"""Write a professional cover letter for the following job application.

APPLICANT PROFILE:
Name: {USER_PROFILE['name']}
Title: {USER_PROFILE['title']}
Summary: {USER_PROFILE['summary']}
Key Skills: {', '.join(USER_PROFILE['skills'][:8])}

JOB DETAILS:
Title: {job.title}
Company: {job.company.name if job.company else 'Unknown'}
Description: {job.description[:2000] if job.description else 'Not available'}

Requirements:
1. Keep it concise (3-4 paragraphs)
2. Highlight relevant experience and skills
3. Show enthusiasm for the role
4. Be professional but personable
5. Include a call to action

Write the cover letter now:"""

    try:
        if provider == "anthropic":
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


def generate_resume_content(job: Job, client, provider: str) -> str:
    """Generate tailored resume using AI"""
    prompt = f"""Create a tailored professional summary and skills section for the following job.

APPLICANT PROFILE:
Name: {USER_PROFILE['name']}
Current Title: {USER_PROFILE['title']}
Original Summary: {USER_PROFILE['summary']}
All Skills: {', '.join(USER_PROFILE['skills'])}

JOB DETAILS:
Title: {job.title}
Company: {job.company.name if job.company else 'Unknown'}
Description: {job.description[:2000] if job.description else 'Not available'}

Requirements:
1. Rewrite the professional summary to highlight relevant experience
2. Reorder skills to prioritize those mentioned in job description
3. Keep summary to 3-4 sentences
4. Be specific about achievements

Output format:
PROFESSIONAL SUMMARY:
[summary]

KEY SKILLS:
[bullet list of top 10 relevant skills]"""

    try:
        if provider == "anthropic":
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.get("/{job_id}", response_model=List[DocumentResponse])
def get_documents(job_id: int, db: Session = Depends(get_db)):
    """Get all generated documents for a job"""
    documents = db.query(GeneratedDocument).filter(
        GeneratedDocument.user_id == DEFAULT_USER_ID,
        GeneratedDocument.job_id == job_id
    ).order_by(GeneratedDocument.created_at.desc()).all()

    return [DocumentResponse.model_validate(doc) for doc in documents]


@router.post("/cover-letter", response_model=DocumentResponse)
def generate_cover_letter(data: DocumentCreate, db: Session = Depends(get_db)):
    """Generate a cover letter for a job"""
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    client, provider = get_ai_client(db)
    if not client:
        raise HTTPException(
            status_code=400,
            detail="No AI API key configured. Please add your Anthropic or OpenAI API key in settings."
        )

    content = generate_cover_letter_content(job, client, provider)

    # Save document
    document = GeneratedDocument(
        user_id=DEFAULT_USER_ID,
        job_id=data.job_id,
        document_type="cover_letter",
        content=content,
        ai_model=f"{provider}"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.post("/resume", response_model=DocumentResponse)
def generate_resume(data: DocumentCreate, db: Session = Depends(get_db)):
    """Generate a tailored resume for a job"""
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    client, provider = get_ai_client(db)
    if not client:
        raise HTTPException(
            status_code=400,
            detail="No AI API key configured. Please add your Anthropic or OpenAI API key in settings."
        )

    content = generate_resume_content(job, client, provider)

    # Save document
    document = GeneratedDocument(
        user_id=DEFAULT_USER_ID,
        job_id=data.job_id,
        document_type="resume",
        content=content,
        ai_model=f"{provider}"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return document
