"""Application-wide configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env_loader import get_env_files, load_env_files

_LOADED_ENV_FILES = load_env_files()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "AlphaForge"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge"

    # ── Auth / JWT ───────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ── LLM Gateway (free multi-provider) ────────
    gemini_api_key: str = ""
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # ── Vector / Memory ──────────────────────────
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    memory_top_k: int = 5
    memory_max_age_days: int = 90

    # ── CORS ─────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Logging ──────────────────────────────────
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "alphaforge.log"
    log_max_bytes: int = 10_485_760  # 10 MB
    log_backup_count: int = 5


settings = Settings()
