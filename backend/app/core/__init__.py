"""
Application Configuration — Pydantic Settings
Loads from .env with type validation and defaults.
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Central configuration for the AI Assessment Engine."""

    # --- Server ---
    PORT: int = 5000
    NODE_ENV: str = "development"

    # --- Database ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./quiz_engine.db"

    # --- LLM Provider ---
    LLM_PROVIDER: str = "groq"  # "groq" | "gemini"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GEMINI_API_KEY: str = ""

    # --- RAG Pipeline ---
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "./data/vector_store"
    UPLOAD_DIR: str = "./data/uploads"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # --- Quiz Defaults ---
    DEFAULT_QUIZ_QUESTIONS: int = 10
    MAX_QUIZ_QUESTIONS: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — read once from .env."""
    return Settings()
