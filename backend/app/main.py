"""Unified FastAPI backend: Education (async) + Analytics (sync) + Golden Mart."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .config import get_settings
from .db_async import BaseAsync, async_session, engine_async
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
from .routes.analytics_ref import router as analytics_ref_router
from .routes.rs_ref import router as rs_ref_router

# Golden Mart (async)
from .routes.gm import router as gm_router

# Register reference models so create_all() picks them up
from . import models_analytics_ref  # noqa: F401
from . import models_rs_ref  # noqa: F401
from . import models_gm  # noqa: F401  — registers Golden Mart tables
from .auth import hash_password
from .models_education import User

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("nbu-unified")

settings = get_settings()


async def ensure_seed_entities() -> None:
    """Auto-seed GM entities (countries, regions, cities) on every startup.
    Idempotent — only inserts entities whose key isn't already in the table.
    Without this the admin panel's "Объект" dropdown is empty.
    """
    from . import models_gm as gm
    SEEDS = [
        # Country
        {"key": "uzbekistan", "level": "country", "parent_key": None,
         "name_ru": "Узбекистан",          "name_uz": "Oʻzbekiston",         "iso_kind": None},
        # Regions (viloyats)
        {"key": "fergana_region", "level": "region", "parent_key": "uzbekistan",
         "name_ru": "Ферганская область",   "name_uz": "Fargʻona viloyati",   "iso_kind": "viloyat"},
        {"key": "samarqand_region", "level": "region", "parent_key": "uzbekistan",
         "name_ru": "Самаркандская область","name_uz": "Samarqand viloyati",  "iso_kind": "viloyat"},
        # Fergana viloyat cities
        {"key": "fargona_city",  "level": "city", "parent_key": "fergana_region",
         "name_ru": "г. Фергана",           "name_uz": "Fargʻona shahri",     "iso_kind": "shahar"},
        {"key": "qoqon_city",    "level": "city", "parent_key": "fergana_region",
         "name_ru": "г. Коканд",            "name_uz": "Qoʻqon shahri",       "iso_kind": "shahar"},
        {"key": "margilon_city", "level": "city", "parent_key": "fergana_region",
         "name_ru": "г. Маргилан",          "name_uz": "Margʻilon shahri",    "iso_kind": "shahar"},
        {"key": "quvasoy_city",  "level": "city", "parent_key": "fergana_region",
         "name_ru": "г. Кувасай",           "name_uz": "Quvasoy shahri",      "iso_kind": "shahar"},
        # Samarkand viloyat cities (room for expansion)
        {"key": "samarqand_city",  "level": "city", "parent_key": "samarqand_region",
         "name_ru": "г. Самарканд",         "name_uz": "Samarqand shahri",    "iso_kind": "shahar"},
        {"key": "kattaqorgon_city", "level": "city", "parent_key": "samarqand_region",
         "name_ru": "г. Каттакурган",       "name_uz": "Kattaqoʻrgʻon shahri","iso_kind": "shahar"},
    ]
    inserted, existed = 0, 0
    async with async_session() as session:
        for seed in SEEDS:
            existing = await session.execute(
                select(gm.GmEntity).where(gm.GmEntity.key == seed["key"])
            )
            if existing.scalar_one_or_none() is None:
                session.add(gm.GmEntity(**seed))
                inserted += 1
            else:
                existed += 1
        await session.commit()
    log.info("[startup] gm_entities: %d inserted, %d already existed", inserted, existed)


async def ensure_seed_admin() -> None:
    """Auto-seed the default admin on startup so Railway has a working admin
    login without needing to run a separate seed step. On every startup,
    ensure a user with email = SEED_ADMIN_EMAIL exists with role='admin'
    and password = hash(SEED_ADMIN_PASSWORD). Env vars become the single
    source of truth for admin login.
    """
    email    = os.getenv("SEED_ADMIN_EMAIL",    "admin@nbu.uz")
    password = os.getenv("SEED_ADMIN_PASSWORD", "admin12345")
    name     = os.getenv("SEED_ADMIN_NAME",     "NBU Admin")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            session.add(User(
                email=email, password_hash=hash_password(password),
                full_name=name, role="admin",
            ))
            await session.commit()
            log.info("[startup] created admin %s (role=admin, password from env)", email)
        else:
            if user.role != "admin":
                user.role = "admin"
            user.password_hash = hash_password(password)
            await session.commit()
            log.info("[startup] admin %s synced (role+password from env)", email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    # Ensure DB schemas in background — don't block startup
    async def _ensure_schemas():
        for attempt in range(1, 6):
            try:
                async with engine_async.begin() as conn:
                    await conn.run_sync(BaseAsync.metadata.create_all)
                log.info("Education + GM DB schema ensured (async).")
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

        # Seed default admin user (idempotent)
        try:
            await ensure_seed_admin()
        except Exception as e:
            log.warning("[startup] admin seed skipped: %s", e)

        # Seed GM entities (countries, regions, cities) — admin panel dropdown
        try:
            await ensure_seed_entities()
        except Exception as e:
            log.warning("[startup] entities seed skipped: %s", e)

        # Seed verified GM data (Qoqon / Fergana / Margilan + Fergana region)
        # ON CONFLICT DO NOTHING — admin edits via panel are preserved.
        try:
            from .seed_gm_data import seed_gm_data
            await seed_gm_data()
        except Exception as e:
            log.warning("[startup] gm data seed skipped: %s", e)

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
app.include_router(rs_ref_router, prefix="/api/rs")
app.include_router(analytics_ref_router)

# Golden Mart routes
app.include_router(gm_router)


@app.get("/health", tags=["meta"])
async def health():
    return {
        "status": "ok",
        "env": settings.app_env,
        "model": settings.anthropic_model_clean,
        "anthropicConfigured": bool(settings.anthropic_api_key_clean),
    }


@app.get("/api/health", tags=["meta"])
async def api_health():
    return {"status": "ok"}


@app.get("/api/health/admin", tags=["meta"])
async def admin_health():
    """Diagnostic — returns whether the seed admin exists in DB without
    exposing password/hash. Lets us verify auto-seed actually ran on
    this deploy.
    """
    email = os.getenv("SEED_ADMIN_EMAIL", "admin@nbu.uz")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
    return {
        "expected_email": email,
        "user_found": user is not None,
        "user_email": user.email if user else None,
        "user_role": user.role if user else None,
        "auto_seed_password_env_set": os.getenv("SEED_ADMIN_PASSWORD") is not None,
    }


@app.post("/api/seed-ref", tags=["meta"])
def seed_reference_data():
    """Seed analytics regions + RS cities/benchmarks. Idempotent — safe to call repeatedly."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    results = {}
    try:
        from seed_rs import seed as seed_rs
        seed_rs()
        results["rs"] = "ok"
    except Exception as e:
        results["rs"] = f"error: {e}"
    try:
        from seed_analytics import seed as seed_analytics
        seed_analytics()
        results["analytics"] = "ok"
    except Exception as e:
        results["analytics"] = f"error: {e}"
    return {"status": "done", "results": results}


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
