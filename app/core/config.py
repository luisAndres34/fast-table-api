from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastTable API"
    ENVIRONMENT: str = "local"

    # Required variables (Loaded strictly from .env)
    DATABASE_URL: str
    SECRET_KEY: str
    
    # Tokens configurations
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_MINUTES: int = 60 * 24 * 7  # 7 days

    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "password123"
    
    # CORS & Services
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    REDIS_URL: str = "redis://redis:6379/0"

    # SMTP Settings for Email Sending (Optional defaults, loaded from .env)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()