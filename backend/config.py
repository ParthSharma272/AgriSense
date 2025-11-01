"""
Configuration settings for AgriSense 2.0
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AgriSense 2.0"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Hugging Face
    HF_API_TOKEN: str = ""
    HF_MODEL: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Database
    DATABASE_URL: str = "postgresql://agrisense_user:password@localhost:5432/agrisense"
    POSTGRES_USER: str = "agrisense_user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "agrisense"
    
    # Vector Store
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Data.gov.in
    DATA_GOV_API_KEY: str = ""
    DATA_GOV_BASE_URL: str = "https://api.data.gov.in/resource"
    
    # Storage
    DATA_DIR: Path = Path(__file__).parent.parent / "data"
    CACHE_DIR: Path = Path(__file__).parent / "cache"
    
    # Mapbox (optional)
    MAPBOX_ACCESS_TOKEN: str = ""
    
    # RAG Settings
    MAX_CONTEXT_LENGTH: int = 4096
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # Visualization
    DEFAULT_CHART_WIDTH: int = 800
    DEFAULT_CHART_HEIGHT: int = 600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
