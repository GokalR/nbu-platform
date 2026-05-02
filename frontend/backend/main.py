"""FastAPI backend for NBU Education Platform."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import Base, engine
import gm_models  # noqa: F401  — registers Golden Mart tables with Base.metadata
from routes.auth_routes import router as auth_router
from routes.courses import router as courses_router
from routes.dashboard import router as dashboard_router
from routes.enrollment import router as enrollment_router
from routes.progress import router as progress_router
from routes.videos import router as videos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="NBU Education API", lifespan=lifespan)

# CORS — allow the Vue dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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


@app.get("/api/health")
async def health():
    return {"status": "ok"}
