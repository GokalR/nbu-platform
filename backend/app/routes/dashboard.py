from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..db_async import get_db
from ..models_education import Course, Enrollment, Progress, User, Video

router = APIRouter(prefix="/api/me", tags=["dashboard"])


def t(field, lang: str) -> str:
    if isinstance(field, dict):
        return field.get(lang, field.get("ru", ""))
    return field or ""


@router.get("/dashboard")
async def get_dashboard(
    lang: str = Query("ru", pattern="^(ru|uz)$"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    enrollments_result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == user.id)
    )
    enrollments = enrollments_result.scalars().all()

    enrolled_courses = []
    for e in enrollments:
        course_result = await db.execute(select(Course).where(Course.id == e.course_id))
        course = course_result.scalar_one_or_none()
        if not course:
            continue

        total_result = await db.execute(
            select(func.count()).select_from(Video).where(Video.course_id == course.id)
        )
        total_videos = total_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count())
            .select_from(Progress)
            .where(
                Progress.user_id == user.id,
                Progress.progress_type == "video",
                Progress.data["completed"].as_boolean() == True,
            )
        )
        completed_videos = completed_result.scalar() or 0

        progress_pct = (completed_videos / total_videos * 100) if total_videos > 0 else 0

        enrolled_courses.append({
            "courseId": str(course.id),
            "title": t(course.title, lang),
            "thumbnailUrl": course.thumbnail_url,
            "educatorName": course.educator_name,
            "totalVideos": total_videos,
            "completedVideos": completed_videos,
            "progressPercent": round(progress_pct),
        })

    scores_result = await db.execute(
        select(Progress)
        .where(
            Progress.user_id == user.id,
            Progress.progress_type.in_(["quiz", "test"]),
        )
        .order_by(Progress.created_at.desc())
        .limit(10)
    )
    scores = [
        {
            "id": str(p.id),
            "type": p.progress_type,
            "scorePercent": p.data.get("score_percent"),
            "passed": p.data.get("passed"),
            "createdAt": p.created_at.isoformat() if p.created_at else None,
        }
        for p in scores_result.scalars().all()
    ]

    return {
        "enrolledCourses": enrolled_courses,
        "recentScores": scores,
        "dueCards": [],
    }


@router.get("/flashcards/due")
async def get_due_flashcards(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    return []
