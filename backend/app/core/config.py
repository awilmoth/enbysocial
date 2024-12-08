from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Enby Social"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/enbysocial"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "enbysocial"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # React default port
        "http://localhost:8000",  # FastAPI default port
        "http://localhost",
        "https://localhost",
        "https://localhost:3000",
    ]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5_242_880  # 5MB in bytes
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png"]
    
    # Geolocation
    DEFAULT_RADIUS_MILES: float = 50.0
    MAX_RADIUS_MILES: float = 100.0
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
