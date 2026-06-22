from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Interior Design AI"
    debug: bool = False

    # API Keys
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interior_design"

    # Object Storage (S3-compatible)
    s3_endpoint: Optional[str] = None
    s3_bucket: str = "interior-design-uploads"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None

    # Model Configuration
    model_provider: str = "anthropic"  # "anthropic", "gemini", "together", "openai", or "local"
    model_name: str = "claude-sonnet-4-20250514"  # Default model

    # Fine-tuned models (set after training on Together AI)
    pinterest_model: Optional[str] = None
    stock_model: Optional[str] = None

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
