"""Unified FastAPI backend: Education (async) + Analytics (sync)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db_async import BaseAsync, engine_async
from .db_sync import BaseSync, engine_sync

# Education routes (async)
from .routes.auth_routes import router as auth_router
from .routes.courses import router as courses_router
from .routes.dashboard import router as dashboard_router
from .routes.enrollment import router as enrollment_router
from .routes.progress import router as progress_router
from .routes.videos import router as videos_router

# Analytics routes (sync)
from .routes.analyze import router as analyze_router
from .routes.excel import router as excel_router
from .routes.submissions import router as submissions_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("nbu-unified")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create education tables (async)
    async with engine_async.begin() as conn:
        await conn.run_sync(BaseAsync.metadata.create_all)
    log.info("Education DB schema ensured (async).")

    # Create analytics tables (sync)
    try:
        BaseSync.metadata.create_all(bind=engine_sync)
        log.info("Analytics DB schema ensured (sync).")
    except Exception as e:
        log.error("Could not ensure analytics DB schema: %s", e)

    yield
    await engine_async.dispose()


app = FastAPI(title="NBU Unified API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Education routes
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(enrollment_router)
app.include_router(videos_router)
app.include_router(progress_router)
app.include_router(dashboard_router)

# Analytics routes — mounted under /api/rs prefix
app.include_router(submissions_router, prefix="/api/rs")
app.include_router(excel_router, prefix="/api/rs")
app.include_router(analyze_router, prefix="/api/rs")


@app.get("/health", tags=["meta"])
async def health():
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.anthropic_model,
        "anthropicConfigured": bool(settings.anthropic_api_key),
    }


@app.get("/api/health", tags=["meta"])
async def api_health():
    return {"status": "ok"}
