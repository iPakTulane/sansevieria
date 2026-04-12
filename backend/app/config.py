import os
from pydantic_settings import BaseSettings


def _parse_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Sansevieria API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sansevieria")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8081,http://127.0.0.1:8081,http://localhost:8080,http://127.0.0.1:8080",
    )
    ANALYTICS_ADMIN_EMAILS: str = os.getenv("ANALYTICS_ADMIN_EMAILS", "test@example.com")
    
    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT: int = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER: str = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD: str = os.getenv("RABBITMQ_PASSWORD", "guest")
    
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))

    LM_STUDIO_BASE_URL: str = os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234")
    LM_STUDIO_CHAT_ENDPOINT: str = os.getenv("LM_STUDIO_CHAT_ENDPOINT", "/v1/chat/completions")
    LM_STUDIO_TIMEOUT: int = int(os.getenv("LM_STUDIO_TIMEOUT", 30))
    LM_STUDIO_MODEL: str = os.getenv("LM_STUDIO_MODEL", "local-model")
    CHATBOT_SYSTEM_PROMPT: str = os.getenv(
        "CHATBOT_SYSTEM_PROMPT",
        "You are Sansevieria Assistant. Help users with plant care, snake plants, product guidance, and related plant questions.",
    )
    
    SIMULATE_PAYMENT_FAILURE: bool = os.getenv("SIMULATE_PAYMENT_FAILURE", "false").lower() == "true"

    @property
    def allowed_origins_list(self) -> list[str]:
        return _parse_csv(self.ALLOWED_ORIGINS)

    @property
    def analytics_admin_emails_set(self) -> set[str]:
        return {email.lower() for email in _parse_csv(self.ANALYTICS_ADMIN_EMAILS)}

    @property
    def lm_studio_chat_url(self) -> str:
        return f"{self.LM_STUDIO_BASE_URL.rstrip('/')}/{self.LM_STUDIO_CHAT_ENDPOINT.lstrip('/')}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
