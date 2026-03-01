from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models.models import SystemSettings
from ..schemas.schemas import SettingUpdate, GoogleChatTest, EmailTest
from ..utils.auth import require_admin
from ..services.google_chat_service import send_google_chat_message
from ..services.email_service import send_email_sync

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/")
def get_all_settings(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Get all system settings."""
    settings = db.query(SystemSettings).all()
    return {s.key: s.value for s in settings}


@router.get("/{key}")
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Get a specific setting."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return {"key": setting.key, "value": setting.value, "description": setting.description}


@router.put("/{key}")
def update_setting(
    key: str,
    setting_in: SettingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Update a system setting."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        setting = SystemSettings(key=key, value=setting_in.value)
        db.add(setting)
    else:
        setting.value = setting_in.value
    db.commit()
    db.refresh(setting)
    return {"key": setting.key, "value": setting.value}


@router.post("/test/email")
def test_email(
    test_in: EmailTest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Test email configuration."""
    success = send_email_sync(
        test_in.to_email,
        test_in.subject,
        f"<p>This is a test email from District IT Help Desk.</p><p>If you received this, your email configuration is working correctly!</p>"
    )
    return {"success": success, "message": "Test email sent" if success else "Failed to send test email"}


@router.post("/test/google-chat")
async def test_google_chat(
    test_in: GoogleChatTest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)
):
    """Test Google Chat webhook configuration."""
    success = await send_google_chat_message(test_in.message)
    return {"success": success, "message": "Test message sent" if success else "Failed to send test message"}
