"""FastAPI backend for NBU Education Platform."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from auth import hash_password
from models import Base, User, async_session, engine
import gm_models  # noqa: F401  — registers Golden Mart tables with Base.metadata
from routes.auth_routes import router as auth_router

log = logging.getLogger("startup")
logging.basicConfig(level=logging.INFO, format="%(message)s")
from routes.courses import router as courses_router
from routes.dashboard import router as dashboard_router
from routes.enrollment import router as enrollment_router
from routes.gm import router as gm_router
from routes.progress import router as progress_router
from routes.videos import router as videos_router


async def ensure_seed_admin() -> None:
    """Auto-seed the default admin on startup so Railway has a working admin
    login without needing to run seed_gm.py manually. Override the defaults
    via env vars before deployment if you want different credentials.
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
            log.info("[startup] created admin %s (role=admin)", email)
        elif user.role != "admin":
            user.role = "admin"
            await session.commit()
            log.info("[startup] promoted %s to admin", email)
        else:
            log.info("[startup] admin %s already exists", email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables + ensure admin user exists on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await ensure_seed_admin()
    except Exception as exc:
        # Don't crash the server if seeding hits an issue — log and continue
        log.warning("[startup] admin seed skipped: %s", exc)
    yield
    await engine.dispose()


app = FastAPI(title="NBU Education API", lifespan=lifespan)

# CORS — dev servers + Cloudflare Pages production + custom domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://nbu-platform.pages.dev",
    ],
    # Allow any *.pages.dev preview deploy
    allow_origin_regex=r"https://.*\.nbu-platform\.pages\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(enrollment_router)
app.include_router(videos_router)
app.include_router(progress_router)
app.include_router(dashboard_router)
app.include_router(gm_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
