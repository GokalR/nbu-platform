import hashlib
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_analytics import AnalysisResult, Submission
from ..schemas import AnalysisOut, AnalysisRequest
from ..services import benchmarks, cities, claude_client

log = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions/{sub_id}/analysis", tags=["analysis"])


def _build_context(sub: Submission, db, rules_score: dict | None, lang: str) -> dict:
    city = cities.resolve(sub.city_id, sub.profile, db=db)

    user_ratios = None
    user_absolutes = None
    latest_excel_hashes = []
    for u in sorted(sub.uploads, key=lambda x: x.created_at, reverse=True):
        if u.file_hash:
            latest_excel_hashes.append(f"{u.kind}:{u.file_hash}")
        computed = (u.parsed or {}).get("computed")
        if computed and user_ratios is None:
            user_ratios = computed.get("ratios")
            user_absolutes = computed.get("absolutes")

    peer_comparison = benchmarks.compare(user_ratios or {}, db=db) if user_ratios else []

    return {
        "lang": lang,
        "profile": sub.profile,
        "finance": sub.finance,
        "city": city,
        "userFinancials": (
            {"ratios": user_ratios, "absolutes": user_absolutes} if user_ratios else None
        ),
        "peerComparison": peer_comparison,
        "rulesScore": rules_score,
        "_excelFingerprints": sorted(latest_excel_hashes),
    }


def _hash_context(ctx: dict) -> str:
    """Canonical hash of context for dedup. Sorted keys, UTF-8."""
    canonical = json.dumps(ctx, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def run_analysis(sub_id: str, body: AnalysisRequest | None = None, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")

    lang = (body and body.lang) or sub.lang or "ru"
    model_override = body.model if body else None
    rules_score = body.rules_score if body else None
    ctx = _build_context(sub, db, rules_score, lang)
    ctx_hash = _hash_context(ctx)

    # Dedup: if a successful analysis already exists for this exact context, return it.
    cached = (
        db.query(AnalysisResult)
        .filter(
            AnalysisResult.submission_id == sub.id,
            AnalysisResult.context_hash == ctx_hash,
            AnalysisResult.error.is_(None),
        )
        .order_by(AnalysisResult.created_at.desc())
        .first()
    )
    if cached:
        log.info("Analysis dedup hit for submission %s (hash %s…)", sub_id, ctx_hash[:8])
        return cached

    try:
        result = claude_client.analyze(ctx, lang=lang, model=model_override)
        rec = AnalysisResult(
            submission_id=sub.id,
            context=ctx,
            context_hash=ctx_hash,
            output=result["output"],
            model=result["model"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        )
    except Exception as e:
        rec = AnalysisResult(
            submission_id=sub.id,
            context=ctx,
            context_hash=ctx_hash,
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
    successful = [a for a in sub.analyses if not a.error]
    if not successful:
        raise HTTPException(404, "No analysis yet for this submission")
    return sorted(successful, key=lambda a: a.created_at, reverse=True)[0]
