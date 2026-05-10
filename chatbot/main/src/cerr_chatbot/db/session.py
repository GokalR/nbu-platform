"""Engine factory. Connection only - no schema creation here."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine

from cerr_chatbot.config import Settings, get_settings


def make_engine(settings: Settings | None = None, **engine_kwargs: object) -> Engine:
    cfg = settings or get_settings()
    return create_engine(cfg.resolved_database_url(), future=True, **engine_kwargs)
