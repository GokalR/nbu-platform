from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user, get_db, require_auth
from models import Course, Enrollment, User

router = APIRouter(prefix="/api/courses", tags=["enrollment"])


@router.get("/{course_id}/enroll")
async def check_enrollment(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    if not user:
        return {"enrolled": False}

    result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course_id,
        )
    )
    enrollment = result.scalar_one_or_none()
    return {"enrolled": enrollment is not None}


@router.post("/{course_id}/enroll")
async def enroll(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    # Check course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already enrolled
    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"enrolled": True, "message": "Already enrolled"}

    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment)
    await db.commit()
    return {"enrolled": True, "message": "Enrolled successfully"}
