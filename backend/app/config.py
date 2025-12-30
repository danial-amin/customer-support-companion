"""Configuration management for the application."""
from pydantic_settings import BaseSettings
from typing import Optional, List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Customer Support AI"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY_HEADER: str = "X-API-Key"
    
    # CORS - can be JSON string or comma-separated
    CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:3001", "http://localhost:3003", "http://localhost:5173"]'
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string."""
        try:
            return json.loads(self.CORS_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            # Fallback to comma-separated
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gpt-4"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # Pinecone Settings
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "customer-support"
    
    # Database Settings (for SQL agent)
    DATABASE_URL: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

