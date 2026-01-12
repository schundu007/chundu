"""
Configuration settings for the Job Search API
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost:5432/job_search"

    # AI APIs
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Job APIs
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    # CORS
    allowed_origins: str = "http://localhost:8000,https://www.sudhakarchundu.org"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
