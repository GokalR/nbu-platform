from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..db_async import get_db
from ..models_education import Progress, User

router = APIRouter(prefix="/api/progress", tags=["progress"])


class VideoProgressRequest(BaseModel):
    video_id: str
    watched_sec: int | None = None
    last_position: int | None = None
    completed: bool | None = None


class QuizProgressRequest(BaseModel):
    content_id: str
    answers: dict
    score_percent: float | None = None


class TestProgressRequest(BaseModel):
    content_id: str
    answers: dict
    score_percent: float | None = None
    passed: bool | None = None


class FlashcardProgressRequest(BaseModel):
    content_id: str
    card_id: str
    rating: int


@router.post("/video")
async def save_video_progress(
    body: VideoProgressRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Progress).where(
            Progress.user_id == user.id,
            Progress.video_id == body.video_id,
            Progress.progress_type == "video",
        )
    )
    progress = result.scalar_one_or_none()

    data = {}
    if body.watched_sec is not None:
        data["watched_sec"] = body.watched_sec
    if body.last_position is not None:
        data["last_position"] = body.last_position
    if body.completed:
        data["completed"] = True

    if progress:
        existing_data = progress.data or {}
        existing_data.update(data)
        progress.data = existing_data
        await db.commit()
    else:
        progress = Progress(
            user_id=user.id,
            video_id=body.video_id,
            progress_type="video",
            data=data,
        )
        db.add(progress)
        await db.commit()

    return {"ok": True}


@router.post("/quiz")
async def save_quiz_progress(
    body: QuizProgressRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    progress = Progress(
        user_id=user.id,
        content_id=body.content_id,
        progress_type="quiz",
        data={
            "answers": body.answers,
            "score_percent": body.score_percent,
        },
    )
    db.add(progress)
    await db.commit()
    return {"ok": True, "score_percent": body.score_percent}


@router.post("/test")
async def save_test_progress(
    body: TestProgressRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    progress = Progress(
        user_id=user.id,
        content_id=body.content_id,
        progress_type="test",
        data={
            "answers": body.answers,
            "score_percent": body.score_percent,
            "passed": body.passed,
        },
    )
    db.add(progress)
    await db.commit()
    return {"ok": True, "score_percent": body.score_percent, "passed": body.passed}


@router.post("/flashcard")
async def save_flashcard_progress(
    body: FlashcardProgressRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    progress = Progress(
        user_id=user.id,
        content_id=body.content_id,
        progress_type="flashcard",
        data={"card_id": body.card_id, "rating": body.rating},
    )
    db.add(progress)
    await db.commit()
    return {"ok": True}
