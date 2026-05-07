from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth_sync import get_current_user_id, require_user_id
from ..db_sync import get_db
from ..models_analytics import AnalysisResult, Submission
from ..schemas import SubmissionCreate, SubmissionOut, SubmissionWithAnalysis

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
def create_submission(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_id),
):
    sub = Submission(
        profile=payload.profile,
        finance=payload.finance,
        city_id=payload.city_id,
        lang=payload.lang,
        user_id=user_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/my", response_model=list[SubmissionWithAnalysis])
def my_submissions(
    db: Session = Depends(get_db),
    user_id: str = Depends(require_user_id),
):
    """Get all submissions for the authenticated user, with latest analysis."""
    subs = (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.created_at.desc())
        .all()
    )
    results = []
    for sub in subs:
        latest = (
            db.query(AnalysisResult)
            .filter(AnalysisResult.submission_id == sub.id)
            .order_by(AnalysisResult.created_at.desc())
            .first()
        )
        results.append(SubmissionWithAnalysis(
            id=sub.id,
            created_at=sub.created_at,
            updated_at=sub.updated_at,
            user_id=sub.user_id,
            profile=sub.profile,
            finance=sub.finance,
            city_id=sub.city_id,
            lang=sub.lang,
            latest_analysis={
                "id": latest.id,
                "verdict": (latest.output or {}).get("verdict"),
                "summary": (latest.output or {}).get("summary"),
                "model": latest.model,
                "created_at": latest.created_at.isoformat(),
                "error": latest.error,
            } if latest else None,
        ))
    return results


@router.get("/{sub_id}", response_model=SubmissionOut)
def get_submission(sub_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")
    return sub


@router.patch("/{sub_id}", response_model=SubmissionOut)
def update_submission(sub_id: str, payload: SubmissionCreate, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")
    sub.profile = payload.profile or sub.profile
    sub.finance = payload.finance or sub.finance
    if payload.city_id is not None:
        sub.city_id = payload.city_id
    if payload.lang:
        sub.lang = payload.lang
    db.commit()
    db.refresh(sub)
    return sub
