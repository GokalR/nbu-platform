from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db
from config import VIDEO_BASE_URL
from models import LearningContent, Video

router = APIRouter(prefix="/api/videos", tags=["videos"])


def t(field, lang: str) -> str:
    """Extract translation from JSONB field."""
    if isinstance(field, dict):
        return field.get(lang, field.get("ru", ""))
    return field or ""


def asset_url(path: str | None) -> str | None:
    """Prepend VIDEO_BASE_URL to asset paths for R2 in production."""
    if not path:
        return path
    if path.startswith("http"):
        return path
    return f"{VIDEO_BASE_URL}{path}" if VIDEO_BASE_URL else path


def translate_content(obj, lang: str):
    """Recursively translate JSONB content."""
    if isinstance(obj, dict):
        if "ru" in obj and "uz" in obj and len(obj) == 2:
            return obj.get(lang, obj.get("ru", ""))
        return {k: translate_content(v, lang) for k, v in obj.items()}
    if isinstance(obj, list):
        return [translate_content(item, lang) for item in obj]
    return obj


@router.get("/{video_id}")
async def get_video(
    video_id: str,
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "id": str(video.id),
        "courseId": str(video.course_id),
        "title": t(video.title, lang),
        "description": t(video.description, lang),
        "videoUrl": asset_url(video.video_url),
        "durationSec": video.duration_sec,
        "transcript": video.transcript,
    }


@router.get("/{video_id}/content")
async def get_video_content(
    video_id: str,
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LearningContent).where(LearningContent.video_id == video_id)
    )
    items = result.scalars().all()

    out = {}
    for item in items:
        out[item.content_type] = translate_content(item.content, lang)
    return out
