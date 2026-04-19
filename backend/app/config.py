"""Unified settings for both education (async) and analytics (sync) backends."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    cors_origins: str = "http://localhost:5173"

    # Railway provides DATABASE_URL as postgresql://...
    database_url: str = "postgresql://edupulse:edupulse@localhost:5432/edupulse"

    # Education auth
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    # Video/thumbnail base URL (Cloudflare R2 in production)
    # Production: https://nbu-videos.devgokal.com
    video_base_url: str = ""

    # Analytics / Claude
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 2000
    max_upload_bytes: int = 5 * 1024 * 1024

    @property
    def anthropic_model_clean(self) -> str:
        return self.anthropic_model.strip()

    @property
    def anthropic_api_key_clean(self) -> str:
        return self.anthropic_api_key.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def async_database_url(self) -> str:
        """Convert DATABASE_URL to asyncpg driver for education backend."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """Convert DATABASE_URL to psycopg driver for analytics backend."""
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and "+psycopg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def video_base_url_stripped(self) -> str:
        return self.video_base_url.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
