"""
Application configuration management.
Handles loading and validating configuration from environment variables and config files.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Leonardo Dashboard API"
    API_DESCRIPTION: str = "Congressional Information Dashboard API"
    
    # Security
    API_KEY: str
    API_KEY_NAME: str = "X-API-Key"
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # External Services
    GOOGLE_CIVIC_API_KEY: str
    GOOGLE_CIVIC_API_URL: str = "https://www.googleapis.com/civicinfo/v2"
    
    # Cache Configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour in seconds
    
    # Data Storage
    DATA_DIR: Path = Path("data")
    COMMITTEE_DATA_FILE: Path = Path("data/committees.json")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "app.log"
    
    @field_validator("DATA_DIR", "COMMITTEE_DATA_FILE")
    @classmethod
    def create_directories(cls, v):
        if isinstance(v, Path):
            v.parent.mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Override model_dump method to handle Path objects"""
        d = super().model_dump(*args, **kwargs)
        return {k: str(v) if isinstance(v, Path) else v for k, v in d.items()}

# Create global settings instance
settings = Settings()