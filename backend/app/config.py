from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "District IT Help Desk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_USE_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Database
    DATABASE_URL: str = "postgresql://helpdesk:helpdesk_password@db:5432/helpdesk_db"

    # SMTP Email Settings
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "helpdesk@district.edu"
    SMTP_FROM_NAME: str = "District IT Help Desk"
    SMTP_USE_TLS: bool = True

    # Google Chat Webhook
    GOOGLE_CHAT_WEBHOOK_URL: Optional[str] = None
    GOOGLE_CHAT_ENABLED: bool = False

    # CVE / NVD Settings
    NVD_API_KEY: Optional[str] = None  # Optional - increases rate limits
    CVE_CHECK_INTERVAL_HOURS: int = 6

    # Agent API Key
    AGENT_API_KEY: str = "CHANGE_THIS_AGENT_API_KEY_IN_PRODUCTION"

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
