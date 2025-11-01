"""
Application configuration settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "NuuR"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database
    DATABASE_URL: str = "postgresql://nuur_user:nuur_password@localhost:5432/nuur_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # JWT
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # SMS Gateway
    SMS_PROVIDER: str = "africastalking"
    AFRICASTALKING_USERNAME: str = ""
    AFRICASTALKING_API_KEY: str = ""
    AFRICASTALKING_SENDER_ID: str = "NuuR"
    
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Email
    EMAIL_PROVIDER: str = "sendgrid"
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@nuur.et"
    FROM_NAME: str = "NuuR Safety Platform"
    
    # Media Storage
    MEDIA_STORAGE: str = "s3"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "nuur-media"
    
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Encryption
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    
    # Anti-Theft Settings
    ANTI_THEFT_DEFAULT_TRACKING_INTERVAL: int = 30
    ANTI_THEFT_DEFAULT_RECORDING_DURATION: int = 5
    ANTI_THEFT_MAX_RECORDING_DURATION: int = 30
    
    # Path Tracking
    PATH_TRACKING_BATCH_SIZE: int = 100
    PATH_TRACKING_MAX_POINTS: int = 50000
    
    # Emergency
    EMERGENCY_SERVICES_PHONE: str = "991,907,939"
    EMERGENCY_API_ENDPOINT: str = ""
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Monitoring
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

