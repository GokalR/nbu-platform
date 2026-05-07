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
    anthropic_model: str = "claude-sonnet-4-6-20250627"
    anthropic_max_tokens: int = 2000
    max_upload_bytes: int = 5 * 1024 * 1024

    # OpenAI (alternative provider for Business Plan tool)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # LLM provider toggle for Business Plan: "claude" | "openai".
    # Other tools (Regional Strategist) stay on Claude regardless.
    llm_provider: str = "claude"

    # AI Advisor (regional analytics chatbot — RAG over 14 viloyats).
    # Independent of openai_model so the Advisor can run on a different model
    # than the Business Plan tool.
    rag_model: str = "gpt-5.1"
    vector_store_id: str = ""
    rag_timeout_sec: int = 180

    # CERR Mahalla Analytics v2 — root of the scraped JSON tree.
    # Local dev: defaults to the in-repo reference data (1.4 GB, gitignored).
    # Production: set CERR_DATA_ROOT to a mounted Railway Volume path.
    cerr_data_root: str = ""

    @property
    def anthropic_model_clean(self) -> str:
        return self.anthropic_model.strip()

    @property
    def anthropic_api_key_clean(self) -> str:
        return self.anthropic_api_key.strip()

    @property
    def openai_model_clean(self) -> str:
        return self.openai_model.strip()

    @property
    def openai_api_key_clean(self) -> str:
        return self.openai_api_key.strip()

    @property
    def llm_provider_clean(self) -> str:
        v = self.llm_provider.strip().lower()
        return v if v in ("claude", "openai") else "claude"

    @property
    def rag_model_clean(self) -> str:
        return self.rag_model.strip() or "gpt-5.1"

    @property
    def vector_store_id_clean(self) -> str:
        return self.vector_store_id.strip()

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

    @property
    def cerr_data_root_resolved(self) -> str:
        """Resolve CERR data root: env override, else fall back to the in-repo
        reference_analytics_platform/cerr_runs/ next to the backend folder."""
        v = (self.cerr_data_root or "").strip()
        if v:
            return v
        # backend/app/config.py -> repo root is parents[2]
        from pathlib import Path
        return str(Path(__file__).resolve().parents[2] / "reference_analytics_platform" / "cerr_runs")


@lru_cache
def get_settings() -> Settings:
    return Settings()
