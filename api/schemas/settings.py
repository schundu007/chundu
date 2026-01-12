"""
Settings Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict


class SettingsUpdate(BaseModel):
    anthropic_api_key: Optional[str] = None
    claude_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    theme: Optional[str] = None


class SettingsResponse(BaseModel):
    anthropic_api_key: Optional[str] = None
    claude_model: Optional[str] = None
    openai_api_key: Optional[str] = None
    theme: Optional[str] = None
    # Mask API keys for security
    has_anthropic_key: bool = False
    has_openai_key: bool = False
