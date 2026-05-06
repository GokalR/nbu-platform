"""Routes for the SME Profile (Business Questionnaire) tool.

Mounted under /api/sme-profile by main.py:
  GET  /api/sme-profile/questions
  GET  /api/sme-profile/lookup?q=...
  GET  /api/sme-profile/address/viloyats
  GET  /api/sme-profile/address/tumans?viloyat=...
  GET  /api/sme-profile/address/mfy?viloyat=...&tuman=...
  POST /api/sme-profile/submissions
  GET  /api/sme-profile/admin/submissions   (admin only)
"""

from __future__ import annotations

import logging
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db_sync import get_db
from ..models_sme_profile import SmeProfileSubmission
from ..services import sme_profile_data as data

log = logging.getLogger(__name__)
settings = get_settings()
_security = HTTPBearer(auto_error=False)


# ── Auth helpers (lightweight, mirrors business_plan.py) ──────────────────

def _decode_token(creds: HTTPAuthorizationCredentials | None) -> dict | None:
    if not creds:
        return None
    try:
        return jwt.decode(
            creds.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        return None


def _optional_user(creds: HTTPAuthorizationCredentials | None = Depends(_security)) -> dict | None:
    return _decode_token(creds)


def _require_admin(creds: HTTPAuthorizationCredentials | None = Depends(_security)) -> dict:
    payload = _decode_token(creds)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def _resolve_user_email(user_id: str | None, db: Session) -> str | None:
    if not user_id:
        return None
    from sqlalchemy import text
    row = db.execute(text("SELECT email FROM users WHERE id = :id"), {"id": user_id}).first()
    return row[0] if row else None


# ── Schemas ───────────────────────────────────────────────────────────────

class ClientInfoIn(BaseModel):
    company_name: str = ""
    director: str = ""
    reg_address: str = ""
    phone: str = ""
    turnover_debit: str = ""
    turnover_credit: str = ""
    turnover_all: str = ""
    shareholders_count: str = ""
    accountant: str = ""
    activity_type: str = ""
    sal_sum: str = ""


class GeneralFormIn(BaseModel):
    company_name: str = ""
    inn: str = ""
    reg_address: str = ""
    charter_type: str = ""
    founders_count: int = 1
    founders: List[str] = []
    director: str = ""
    phone: str = ""
    activity_type: str = ""
    turnover_all: str = ""
    turnover_debit: str = ""
    turnover_credit: str = ""
    shareholders_count: str = ""
    accountant: str = ""
    sal_sum: str = ""
    related_companies_count: int = 0
    related_companies_inns: List[str] = []
    credits_count: int = 0
    credit_amount: str = ""
    sphere_count: int = 1


class AnswerIn(BaseModel):
    question_id: str
    question_text_ru: str = ""
    question_text_uz: str = ""
    answer: str = ""


class SphereIn(BaseModel):
    sphere_number: int
    category_id: str
    category_name_ru: str = ""
    category_name_uz: str = ""
    answers: List[AnswerIn]


class SubmissionIn(BaseModel):
    pinfl_or_inn: str
    sphere_count: int
    spheres: List[SphereIn]
    client_info: Optional[ClientInfoIn] = None
    general_form: Optional[GeneralFormIn] = None

    @validator("pinfl_or_inn")
    def _v_pinfl(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("PINFL/INN must not be empty")
        return v.strip()

    @validator("sphere_count")
    def _v_count(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("sphere_count must be between 1 and 10")
        return v


# ── Router ────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/sme-profile", tags=["sme-profile"])


@router.get("/questions")
def get_questions() -> dict:
    return {"categories": data.load_questions()}


@router.get("/lookup")
def lookup(q: str = Query(..., description="PINFL or INN")) -> dict:
    db = data.load_client_db()
    key = q.strip()
    if key.endswith(".0"):
        key = key[:-2]
    record = db.get(key)
    if not record:
        return {"found": False}
    return {"found": True, **record}


@router.get("/address/viloyats")
def get_viloyats() -> dict:
    d = data.load_address_data()
    if not d:
        return {"viloyats": [], "source_found": False}
    return {"viloyats": sorted(d.keys()), "source_found": True}


@router.get("/address/tumans")
def get_tumans(viloyat: str = Query(...)) -> dict:
    d = data.load_address_data()
    return {"tumans": sorted(d.get(viloyat, {}).keys())}


@router.get("/address/mfy")
def get_mfy(viloyat: str = Query(...), tuman: str = Query(...)) -> dict:
    d = data.load_address_data()
    return {"mfy": sorted(d.get(viloyat, {}).get(tuman, []))}


@router.post("/submissions")
def submit(
    payload: SubmissionIn,
    db: Session = Depends(get_db),
    user: dict | None = Depends(_optional_user),
) -> dict:
    # Validate categories exist
    available = {c["id"] for c in data.load_questions()}
    for s in payload.spheres:
        if s.category_id not in available:
            raise HTTPException(
                status_code=400,
                detail=f"Category '{s.category_id}' not found",
            )

    user_email = _resolve_user_email(user.get("sub") if user else None, db)

    row = SmeProfileSubmission(
        user_email=user_email,
        pinfl_or_inn=payload.pinfl_or_inn,
        sphere_count=payload.sphere_count,
        client_info=(payload.client_info.model_dump() if payload.client_info else None),
        general_form=(payload.general_form.model_dump() if payload.general_form else None),
        spheres=[s.model_dump() for s in payload.spheres],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "saved", "id": row.id, "pinfl_or_inn": row.pinfl_or_inn}


# ── Admin: list submissions ───────────────────────────────────────────────

admin_router = APIRouter(prefix="/admin/sme-profile", tags=["sme-profile-admin"])


@admin_router.get("/submissions")
def admin_list(
    db: Session = Depends(get_db),
    _admin: dict = Depends(_require_admin),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    from sqlalchemy import select, func
    total = db.execute(select(func.count(SmeProfileSubmission.id))).scalar() or 0
    rows = db.execute(
        select(SmeProfileSubmission)
        .order_by(SmeProfileSubmission.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return {
        "total": int(total),
        "items": [
            {
                "id": r.id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "user_email": r.user_email,
                "pinfl_or_inn": r.pinfl_or_inn,
                "sphere_count": r.sphere_count,
                "company_name": (r.client_info or {}).get("company_name", ""),
                "spheres": r.spheres,
                "client_info": r.client_info,
                "general_form": r.general_form,
            }
            for r in rows
        ],
    }
