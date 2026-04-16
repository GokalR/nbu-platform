from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_analytics import Submission
from ..schemas import SubmissionCreate, SubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
def create_submission(payload: SubmissionCreate, db: Session = Depends(get_db)):
    sub = Submission(
        profile=payload.profile,
        finance=payload.finance,
        city_id=payload.city_id,
        lang=payload.lang,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


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
