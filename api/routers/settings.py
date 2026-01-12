"""
Settings router - Manage user settings
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict

from ..database import get_db
from ..models import UserSetting
from ..schemas.settings import SettingsUpdate, SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])

# Default user ID for single-user mode
DEFAULT_USER_ID = 1


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get user settings"""
    settings = db.query(UserSetting).filter(
        UserSetting.user_id == DEFAULT_USER_ID
    ).all()

    result = SettingsResponse()
    for setting in settings:
        if setting.setting_key == "anthropic_api_key":
            result.has_anthropic_key = bool(setting.setting_value)
            # Don't expose full key
        elif setting.setting_key == "openai_api_key":
            result.has_openai_key = bool(setting.setting_value)
        elif setting.setting_key == "claude_model":
            result.claude_model = setting.setting_value
        elif setting.setting_key == "theme":
            result.theme = setting.setting_value

    return result


@router.put("", response_model=SettingsResponse)
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db)):
    """Update user settings"""
    settings_map = {
        "anthropic_api_key": data.anthropic_api_key,
        "openai_api_key": data.openai_api_key,
        "claude_model": data.claude_model,
        "theme": data.theme
    }

    for key, value in settings_map.items():
        if value is not None:
            existing = db.query(UserSetting).filter(
                UserSetting.user_id == DEFAULT_USER_ID,
                UserSetting.setting_key == key
            ).first()

            if existing:
                existing.setting_value = value
            else:
                setting = UserSetting(
                    user_id=DEFAULT_USER_ID,
                    setting_key=key,
                    setting_value=value
                )
                db.add(setting)

    db.commit()
    return get_settings(db)


@router.delete("")
def clear_settings(db: Session = Depends(get_db)):
    """Clear all user settings"""
    db.query(UserSetting).filter(
        UserSetting.user_id == DEFAULT_USER_ID
    ).delete()
    db.commit()
    return {"message": "Settings cleared"}
