from pydantic_settings import BaseSettings
from typing import Optional
import os

# Added Settings class in config.py
class Settings(BaseSettings):
    # ... existing config ...
    
    # Database for conversation history
    DATABASE_URL: str = "sqlite:///./data/conversations.db"
    ENABLE_HISTORY: bool = True
    HISTORY_RETENTION_DAYS: int = 30

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "TUK-ConvoSearch"
    VERSION: str = "1.0.0"
    
    # Paths
    DATA_DIR: str = "data"
    RAW_DOCS_DIR: str = "data/raw"
    PROCESSED_DIR: str = "data/processed"
    VECTOR_DB_PATH: str = "data/vector_db"
    
    # Model Config
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Lightweight, good quality
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # LLM Config
    LLM_PROVIDER: str = "ollama"  # "openai", "ollama", "huggingface"
    LLM_MODEL: str = "llama2"  # or "mistral", "gpt-3.5-turbo"
    
    # API Keys (load from .env)
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Retrieval
    TOP_K_RESULTS: int = 4
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"

settings = Settings()