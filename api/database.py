"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import get_settings

settings = get_settings()

# Handle Railway's DATABASE_URL format (may use postgres:// instead of postgresql://)
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist"""
    from . import models  # Import models to register them
    Base.metadata.create_all(bind=engine)

    # Seed default user if not exists
    db = SessionLocal()
    try:
        from .models import UserProfile
        existing = db.query(UserProfile).first()
        if not existing:
            user = UserProfile(
                name="Sudhakar Chundu",
                title="Cloud AI Architect",
                email="chundubabu@gmail.com",
                linkedin="https://www.linkedin.com/in/schundu",
                github="https://github.com/schundu007",
                website="https://www.sudhakarchundu.org",
                location="United States",
                summary="Cloud AI Architect with 18+ years of experience in enterprise infrastructure, AI/ML platforms, and DevOps transformation."
            )
            db.add(user)
            db.commit()
    finally:
        db.close()
