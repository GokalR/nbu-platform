from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db_async import get_db
from ..helpers import translate_field as t, asset_url, translate_content
from ..models_education import LearningContent, Video

router = APIRouter(prefix="/api/videos", tags=["videos"])


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
