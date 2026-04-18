from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_analytics import AnalysisResult, Submission
from ..schemas import AnalysisOut, AnalysisRequest
from ..services import benchmarks, cities, claude_client

import logging
log = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions/{sub_id}/analysis", tags=["analysis"])


def _build_context(sub: Submission) -> dict:
    city = cities.resolve(sub.city_id, sub.profile)

    user_ratios = None
    user_absolutes = None
    for u in sorted(sub.uploads, key=lambda x: x.created_at, reverse=True):
        computed = (u.parsed or {}).get("computed")
        if computed:
            user_ratios = computed.get("ratios")
            user_absolutes = computed.get("absolutes")
            break

    peer_comparison = benchmarks.compare(user_ratios or {}) if user_ratios else []

    return {
        "lang": sub.lang,
        "profile": sub.profile,
        "finance": sub.finance,
        "city": city,
        "userFinancials": (
            {"ratios": user_ratios, "absolutes": user_absolutes} if user_ratios else None
        ),
        "peerComparison": peer_comparison,
    }


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def run_analysis(sub_id: str, body: AnalysisRequest | None = None, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")

    lang = (body and body.lang) or sub.lang or "ru"
    model_override = body.model if body else None
    ctx = _build_context(sub)

    try:
        result = claude_client.analyze(ctx, lang=lang, model=model_override)
        rec = AnalysisResult(
            submission_id=sub.id,
            context=ctx,
            output=result["output"],
            model=result["model"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        )
    except Exception as e:
        rec = AnalysisResult(
            submission_id=sub.id,
            context=ctx,
            output={},
            model=model_override or "unknown",
            input_tokens=0,
            output_tokens=0,
            error=str(e),
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        log.error("Claude analysis failed for submission %s: %s", sub_id, e)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Analysis service temporarily unavailable")

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/latest", response_model=AnalysisOut)
def latest_analysis(sub_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")
    if not sub.analyses:
        raise HTTPException(404, "No analysis yet for this submission")
    return sorted(sub.analyses, key=lambda a: a.created_at, reverse=True)[0]
