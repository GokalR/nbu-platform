"""Unified FastAPI backend: Education (async) + Analytics (sync)."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
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
    import asyncio

    # Ensure DB schemas in background — don't block startup
    async def _ensure_schemas():
        for attempt in range(1, 6):
            try:
                async with engine_async.begin() as conn:
                    await conn.run_sync(BaseAsync.metadata.create_all)
                log.info("Education DB schema ensured (async).")
                break
            except Exception as e:
                log.warning("DB connect attempt %d/5 failed: %s", attempt, e)
                if attempt < 5:
                    await asyncio.sleep(2 * attempt)
                else:
                    log.error("Could not connect to database after 5 attempts.")

        try:
            BaseSync.metadata.create_all(bind=engine_sync)
            log.info("Analytics DB schema ensured (sync).")
        except Exception as e:
            log.error("Could not ensure analytics DB schema: %s", e)

    asyncio.create_task(_ensure_schemas())
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


@app.post("/api/seed", tags=["meta"])
async def run_seed():
    """One-time endpoint to seed education data. Only works in dev/staging."""
    if settings.app_env == "production":
        raise HTTPException(status_code=403, detail="Seed endpoint disabled in production")
    from .db_async import async_session
    from .models_education import Course, Video, LearningContent

    # Import seed data
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from seed import COURSE_1, COURSE_1_VIDEOS, make_quiz, make_flashcards, make_mind_map, make_test

    async with async_session() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        count = (await db.execute(select(func.count()).select_from(Course))).scalar()
        if count > 0:
            return {"status": "already_seeded", "courses": count}

        course = Course(
            title=COURSE_1["title"],
            description=COURSE_1["description"],
            thumbnail_url=COURSE_1["thumbnail_url"],
            category=COURSE_1["category"],
            educator_name=COURSE_1["educator_name"],
            is_published=True,
            sort_order=0,
        )
        db.add(course)
        await db.flush()

        for i, ep in enumerate(COURSE_1_VIDEOS):
            video = Video(
                course_id=course.id,
                title=ep["title"],
                description=ep["description"],
                video_url=ep["video_url"],
                duration_sec=ep["duration_sec"],
                sort_order=i,
            )
            db.add(video)
            await db.flush()

            topic_ru = ep["title"]["ru"].split(": ", 1)[-1] if ": " in ep["title"]["ru"] else ep["title"]["ru"]
            topic_uz = ep["title"]["uz"].split(": ", 1)[-1] if ": " in ep["title"]["uz"] else ep["title"]["uz"]

            for content_type, content_fn in [
                ("quiz", make_quiz),
                ("flashcards", make_flashcards),
                ("mental_map", make_mind_map),
                ("test", make_test),
            ]:
                db.add(LearningContent(video_id=video.id, content_type=content_type, content=content_fn(topic_ru, topic_uz)))

        await db.commit()
        return {"status": "seeded", "courses": 1, "videos": len(COURSE_1_VIDEOS)}
