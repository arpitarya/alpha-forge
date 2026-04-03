"""Application-wide configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "AlphaForge"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    api_v1_prefix: str = "/api/v1"

    # ── Server ───────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge"

    # ── Redis ────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Auth / JWT ───────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ── AI / LLM ────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ── Indian Broker: Zerodha Kite ──────────────
    kite_api_key: str = ""
    kite_api_secret: str = ""

    # ── CORS ─────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Celery ───────────────────────────────────
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"


settings = Settings()
