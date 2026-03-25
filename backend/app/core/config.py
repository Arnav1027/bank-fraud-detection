"""Core configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Database (use SQLite for local dev, PostgreSQL for production)
    DATABASE_URL: str = "sqlite:///./fraud_detection.db"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Bank Fraud Detection"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML
    MODEL_PATH: str = "./app/ml/models/best_model.joblib"
    PREPROCESSING_PATH: str = "./app/ml/models/preprocessor.joblib"
    FRAUD_THRESHOLD: float = 0.5
    
    # CORS - Allow all origins in production (Railway will have dynamic domain)
    CORS_ORIGINS: list = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
