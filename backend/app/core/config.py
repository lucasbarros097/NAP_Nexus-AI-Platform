"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "NAP - Nexus AI Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://nap_user:nap_pass@localhost:5432/nap_nexus"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "nap_knowledge"

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "deepseek/deepseek-chat:free"
    OPENROUTER_MAX_TOKENS: int = 8192
    OPENROUTER_TEMPERATURE: float = 0.7

    # Workspace
    WORKSPACE_DIR: str = "/workspace"
    AGENTS_DIR: str = "/agents"
    MCP_DIR: str = "/mcp"
    LOGS_DIR: str = "/logs"
    KNOWLEDGE_DIR: str = "/knowledge"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()