import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://edupulse:edupulse@localhost:5432/edupulse",
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Base URL for video/thumbnail files (e.g. "https://videos.nbu-testing.devgokal.com")
# Empty in local dev (served from Vite public/), set in production for R2.
VIDEO_BASE_URL = os.getenv("VIDEO_BASE_URL", "").rstrip("/")
