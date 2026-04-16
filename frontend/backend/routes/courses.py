from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_db
from config import VIDEO_BASE_URL
from models import Course, Video

router = APIRouter(prefix="/api/courses", tags=["courses"])


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


@router.get("")
async def list_courses(
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Course)
        .where(Course.is_published == True)
        .order_by(Course.sort_order, Course.created_at.desc())
    )
    courses = result.scalars().all()

    out = []
    for c in courses:
        video_count = await db.execute(
            select(func.count()).select_from(Video).where(Video.course_id == c.id)
        )
        out.append({
            "id": str(c.id),
            "title": t(c.title, lang),
            "description": t(c.description, lang),
            "thumbnailUrl": asset_url(c.thumbnail_url),
            "category": t(c.category, lang),
            "educatorName": c.educator_name,
            "videoCount": video_count.scalar() or 0,
        })
    return out


@router.get("/{course_id}")
async def get_course(
    course_id: str,
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    video_count = await db.execute(
        select(func.count()).select_from(Video).where(Video.course_id == course.id)
    )
    return {
        "id": str(course.id),
        "title": t(course.title, lang),
        "description": t(course.description, lang),
        "thumbnailUrl": course.thumbnail_url,
        "category": t(course.category, lang),
        "educatorName": course.educator_name,
        "videoCount": video_count.scalar() or 0,
        "isPublished": course.is_published,
    }


@router.get("/{course_id}/videos")
async def get_course_videos(
    course_id: str,
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Video)
        .where(Video.course_id == course_id)
        .order_by(Video.sort_order)
    )
    videos = result.scalars().all()
    return [
        {
            "id": str(v.id),
            "title": t(v.title, lang),
            "description": t(v.description, lang),
            "videoUrl": asset_url(v.video_url),
            "durationSec": v.duration_sec,
            "sortOrder": v.sort_order,
        }
        for v in videos
    ]
