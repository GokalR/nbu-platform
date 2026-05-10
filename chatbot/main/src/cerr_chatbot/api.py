"""HTTP wrapper exposing the cerr-chatbot Pipeline as a FastAPI service.

Mirrors `cli._build_runtime_pipeline` for engine/planner construction so the
HTTP and CLI runtimes stay in sync. The pipeline is built lazily on the first
chat request so `/health` succeeds even before the database is reachable.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from cerr_chatbot import __version__
from cerr_chatbot.config import Settings, get_settings
from cerr_chatbot.query import Pipeline

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)
    max_rows: int = Field(default=10, ge=1, le=100)


def _build_pipeline(settings: Settings) -> Pipeline:
    from cerr_chatbot.db.session import make_engine
    from cerr_chatbot.query import (
        make_evidence_planner_from_settings,
        make_pipeline_from_settings,
        make_planner_from_settings,
    )

    engine = make_engine()
    mode = (settings.query_pipeline_mode or "legacy").strip().lower()
    if mode == "evidence":
        return make_pipeline_from_settings(
            engine,
            evidence_planner=make_evidence_planner_from_settings(settings),
            settings=settings,
        )
    return make_pipeline_from_settings(
        engine,
        legacy_planner=make_planner_from_settings(settings),
        settings=settings,
    )


def _get_pipeline(app: FastAPI) -> Pipeline:
    pipeline: Pipeline | None = getattr(app.state, "pipeline", None)
    if pipeline is not None:
        return pipeline
    lock: threading.Lock = app.state.pipeline_lock
    with lock:
        pipeline = getattr(app.state, "pipeline", None)
        if pipeline is None:
            pipeline = _build_pipeline(get_settings())
            app.state.pipeline = pipeline
            logger.info("cerr-chatbot pipeline initialised")
    return pipeline


def create_app() -> FastAPI:
    app = FastAPI(title="cerr-chatbot", version=__version__)
    app.state.pipeline_lock = threading.Lock()
    app.state.pipeline = None

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": "cerr-chatbot", "version": __version__}

    @app.post("/chat")
    def chat(req: ChatRequest) -> dict[str, Any]:
        try:
            pipeline = _get_pipeline(app)
        except Exception as exc:
            logger.exception("pipeline initialisation failed")
            raise HTTPException(status_code=503, detail=f"pipeline_unavailable: {exc}") from exc

        settings = get_settings()
        include_debug = (settings.app_env or "dev").strip().lower() != "prod"
        try:
            return pipeline.answer(
                req.message,
                max_rows=req.max_rows,
                include_debug=include_debug,
                session_id=req.session_id,
            )
        except Exception as exc:
            logger.exception("pipeline.answer failed")
            raise HTTPException(status_code=500, detail=f"pipeline_error: {exc}") from exc

    return app


app = create_app()
