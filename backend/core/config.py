"""Core Configuration and Application Settings"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Review Conflict Resolver"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_SECRET_KEY: str = "change-this-to-a-secure-random-secret-key-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./review_conflict_resolver.db"

    # Vector Embeddings
    VECTOR_DIMENSION: int = 384
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    USE_LOCAL_TRANSFORMERS: bool = False  # Set to True when weights are downloaded locally

    # Background Processing
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    ASYNC_PROCESSING_MODE: str = "in_process"

    # External LLM Providers
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    DEFAULT_LLM_PROVIDER: str = "gemini"
    LLM_TIMEOUT_SECONDS: int = 45
    LLM_MAX_RETRIES: int = 3

    # Data Acquisition & Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 30
    ALLOW_SCRAPING: bool = False
    MOCK_DATA_FALLBACK: bool = True

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
