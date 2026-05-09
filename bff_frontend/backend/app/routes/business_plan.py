"""Routes for SME Business Plan generation + admin review."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db_sync import SessionLocal, get_db
from ..models_business_plan import BusinessPlanSubmission
from ..services import (
    business_plan_client,
    business_plan_validation,
    credit_scoring,
    docx_builder,
    excel_parser_msb,
    nbu_products,
)

log = logging.getLogger(__name__)
settings = get_settings()
_security = HTTPBearer(auto_error=False)


# ---------- auth helpers (sync, lightweight — same pattern as auth_sync) ----------

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


def _require_user(creds: HTTPAuthorizationCredentials | None = Depends(_security)) -> dict:
    payload = _decode_token(creds)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    return payload


def _require_admin(creds: HTTPAuthorizationCredentials | None = Depends(_security)) -> dict:
    payload = _decode_token(creds)
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


# Resolve user_email from sub (user_id) — keeps the route sync without a DB hop
# unless we really need it. We pull email lazily in generate().
def _resolve_user_email(user_id: str | None, db: Session) -> str | None:
    if not user_id:
        return None
    # User table is in the async metadata, but the underlying table is the
    # same DB. Use raw SQL through the sync session to avoid pulling in async.
    from sqlalchemy import text
    row = db.execute(text("SELECT email FROM users WHERE id = :id"), {"id": user_id}).first()
    return row[0] if row else None


# ---------- request / response schemas ----------

class OrganizationIn(BaseModel):
    type: str = Field(..., description="legal_entity | individual")
    inn: str | None = None
    uniqueCode: str | None = None
    name: str
    address: str | None = None
    foundedDate: str | None = None
    mainActivity: str | None = None
    founder: str | None = None
    director: str | None = None
    charterCapital: float | None = 0


class ProjectIn(BaseModel):
    purpose: str
    location: str | None = None
    ownContribution: float = 0
    loanAmount: float = 0
    totalValue: float = 0
    startupMonths: int = 3
    termMonths: int = 36
    graceMonths: int = 6
    interestRate: float = 24.0


class AssetRow(BaseModel):
    name: str
    qty: float = 0
    unit: str | None = None


class ProductRow(BaseModel):
    name: str
    monthlyVolume: float = 0
    unit: str | None = None
    price: float = 0
    currency: str = "UZS"


class TeamRow(BaseModel):
    role: str
    count: int = 0
    salary: float = 0


class UtilityExtra(BaseModel):
    name: str
    amount: float = 0


class UtilitiesIn(BaseModel):
    electricityKwh: float = 0
    gasM3: float = 0
    waterM3: float = 0
    extras: list[UtilityExtra] = []


class GenerateRequest(BaseModel):
    lang: str = "uz"
    organization: OrganizationIn
    project: ProjectIn
    assets: dict[str, list[AssetRow]] = Field(
        default_factory=lambda: {"creditFinanced": [], "selfFinanced": []}
    )
    products: list[ProductRow] = []
    team: list[TeamRow] = []
    utilities: UtilitiesIn = Field(default_factory=UtilitiesIn)


class GenerateResponse(BaseModel):
    id: str
    output: dict[str, Any]
    recommendedProductsCandidates: list[dict[str, Any]]
    creditScore: dict[str, Any] | None = None


class AdminListItem(BaseModel):
    id: str
    createdAt: str
    userEmail: str | None
    lang: str
    orgName: str | None
    orgType: str | None
    inputTokens: int
    outputTokens: int
    hasError: bool


# ---------- routes ----------

router = APIRouter(prefix="/business-plan", tags=["business-plan"])


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_201_CREATED)
def generate(
    body: GenerateRequest,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(_require_user),
):
    """Generate a business plan via Claude and persist the submission."""
    user_id = auth_payload.get("sub")
    user_email = _resolve_user_email(user_id, db)

    inputs_dict = body.model_dump()
    candidates = nbu_products.select_candidates(
        loan_amount_uzs=body.project.loanAmount or 0,
        term_months=body.project.termMonths or 0,
        client_type=body.organization.type,
        assets_credit=[a.model_dump() for a in body.assets.get("creditFinanced", [])],
        project_purpose=body.project.purpose,
        top_n=3,
    )

    # Pre-compute deterministic baseline (ФОТ, utilities, loan annuity, etc.)
    # — used both for credit scoring and for the LLM prompt.
    from ..services import business_plan_compute as bpc
    baseline = bpc.compute_baseline(inputs_dict)

    # Always run wizard-only credit scoring. No Excel uploads — purely
    # derived from anketa inputs (revenue projection, costs, loan terms,
    # equity contribution, business age).
    credit_score = credit_scoring.compute_wizard_score(inputs_dict, baseline)

    # Input gate — refuse to call the LLM if the wizard payload can't
    # produce a meaningful plan. Saves 60-90s on garbage in.
    errors, warnings = business_plan_validation.validate_inputs(
        inputs_dict, baseline, candidates,
    )
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "invalid_inputs", "errors": errors, "warnings": warnings},
        )

    rec = BusinessPlanSubmission(
        user_email=user_email,
        lang=body.lang or "uz",
        org_name=body.organization.name,
        org_type=body.organization.type,
        inputs=inputs_dict,
        recommended_products=candidates,
        # Reuse the existing historical_financials JSONB column to store
        # the credit score blob — no DB migration needed.
        historical_financials=credit_score,
        model="",
    )

    try:
        result = business_plan_client.generate_business_plan(
            inputs=inputs_dict,
            candidate_products=candidates,
            lang=body.lang or "uz",
            historical_financials={"score": credit_score},
            baseline=baseline,
        )
        # Output validator — strips hallucinated products, forces verdict to
        # match deterministic credit score, replaces broken projection with
        # a synthesized ramp, enforces enums on risks/kpis, blanks
        # marketContext if it contains unverifiable quantitative claims.
        rec.output = business_plan_validation.validate_and_clean(
            result["output"],
            candidates=candidates,
            baseline=baseline,
            credit_score=credit_score,
            inputs=inputs_dict,
            warnings=warnings,
        )
        # Stash provider in the model string so admin can see which LLM ran:
        # e.g. "openai/gpt-4o" or "claude/claude-sonnet-4-6-20250627".
        rec.model = f"{result.get('provider', 'unknown')}/{result['model']}"
        rec.input_tokens = result["input_tokens"]
        rec.output_tokens = result["output_tokens"]
    except Exception as e:
        rec.error = str(e)
        db.add(rec)
        db.commit()
        db.refresh(rec)
        log.exception("Business plan generation failed")
        # Surface a short version of the actual error so the frontend can show
        # something useful and admin can debug without grepping Railway logs.
        # Keep it ≤200 chars to avoid leaking large stack traces / prompt content.
        msg = str(e)[:200] or "Unknown error"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Business plan generation failed: {msg}",
        )

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return GenerateResponse(
        id=rec.id,
        output=rec.output,
        recommendedProductsCandidates=rec.recommended_products,
        creditScore=credit_score,
    )


# ---------- streaming variant (SSE) ----------

# Sections that appear in the slim LLM output, in approximately the order the
# model writes them. We emit a progress event as each section's key appears in
# the streamed text — the user sees "Анализ рынка..." → "Идентификация рисков..."
# → "Подбор кредита..." instead of a frozen spinner.
_LLM_SECTION_ORDER: list[tuple[str, int]] = [
    ("summary", 22),
    ("executiveSummary", 30),
    ("marketContext", 40),
    ("operations", 48),
    ("teamAssessment", 55),
    ("financialsAssessment", 60),
    ("extrasCategorization", 65),
    ("milestones", 72),
    ("risks", 80),
    ("kpis", 86),
    ("recommendedProducts", 90),
    ("actionableNextSteps", 94),
]


def _sse(payload: dict) -> bytes:
    """Format a dict as a Server-Sent Events `data:` frame."""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")


@router.post("/generate-stream")
def generate_stream(
    body: GenerateRequest,
    auth_payload: dict = Depends(_require_user),
):
    """Same as /generate, but streams progress to the client via SSE.

    Wall time is unchanged from /generate — this is a UX improvement: the
    user sees a live progress bar moving from validation → scoring → "Анализ
    рисков" → "Подбор кредита" → done, instead of a frozen 60-second
    spinner. The frontend wizard uses this; admin tooling and other callers
    keep using /generate.

    Note: we deliberately do not use `Depends(get_db)` because the route
    keeps an open DB session for the entire stream lifetime. Instead we
    open a session manually inside the generator and close it on exit.
    """
    user_id = auth_payload.get("sub")
    inputs_dict = body.model_dump()

    def event_stream():
        try:
            yield _sse({"phase": "validate", "pct": 5})

            # Pre-compute (deterministic, < 50ms total)
            candidates = nbu_products.select_candidates(
                loan_amount_uzs=body.project.loanAmount or 0,
                term_months=body.project.termMonths or 0,
                client_type=body.organization.type,
                assets_credit=[a.model_dump() for a in body.assets.get("creditFinanced", [])],
                project_purpose=body.project.purpose,
                top_n=3,
            )
            yield _sse({"phase": "candidates", "pct": 10})

            from ..services import business_plan_compute as bpc
            baseline = bpc.compute_baseline(inputs_dict)
            credit_score = credit_scoring.compute_wizard_score(inputs_dict, baseline)
            yield _sse({"phase": "scoring", "pct": 15})

            # Input gate
            errors, warnings = business_plan_validation.validate_inputs(
                inputs_dict, baseline, candidates,
            )
            if errors:
                yield _sse({"phase": "error", "code": "invalid_inputs",
                            "errors": errors, "warnings": warnings})
                return

            yield _sse({"phase": "llm.start", "pct": 18})

            # Stream the LLM. We accumulate text and detect when each known
            # JSON section's key first appears, emitting a progress event.
            output_text = ""
            seen_sections: set[str] = set()
            input_tokens = output_tokens = 0
            model_used = provider_used = ""

            for chunk in business_plan_client.stream_business_plan(
                inputs=inputs_dict,
                candidate_products=candidates,
                lang=body.lang or "uz",
                historical_financials={"score": credit_score},
                baseline=baseline,
            ):
                if chunk.get("type") == "delta":
                    output_text += chunk["text"]
                    # Emit one section event per known key the moment we
                    # see its `"<key>":` appear in the JSON the LLM is
                    # writing. Order in _LLM_SECTION_ORDER controls pct.
                    for section, pct in _LLM_SECTION_ORDER:
                        if section in seen_sections:
                            continue
                        if f'"{section}"' in output_text:
                            seen_sections.add(section)
                            yield _sse({"phase": "llm.section",
                                        "section": section, "pct": pct})
                            break
                elif chunk.get("type") == "complete":
                    output_text = chunk["fullText"]
                    input_tokens = chunk["input_tokens"]
                    output_tokens = chunk["output_tokens"]
                    model_used = chunk["model"]
                    provider_used = chunk["provider"]

            yield _sse({"phase": "finalize", "pct": 96})

            # Parse + assemble + validate
            assembled = business_plan_client.assemble_plan_from_raw(
                raw_text=output_text,
                baseline=baseline,
                credit_score=credit_score,
                candidates=candidates,
                project=inputs_dict.get("project") or {},
            )
            if assembled is None:
                log.error("Stream: LLM returned non-JSON. First 500 chars: %s",
                          output_text[:500])
                yield _sse({"phase": "error", "code": "llm_unparseable",
                            "message": "LLM returned non-JSON"})
                return

            cleaned = business_plan_validation.validate_and_clean(
                assembled,
                candidates=candidates,
                baseline=baseline,
                credit_score=credit_score,
                inputs=inputs_dict,
                warnings=warnings,
            )

            # Persist with a fresh session (Depends() doesn't work inside
            # generators — we'd race the dep cleanup).
            with SessionLocal() as db:
                user_email = _resolve_user_email(user_id, db)
                rec = BusinessPlanSubmission(
                    user_email=user_email,
                    lang=body.lang or "uz",
                    org_name=body.organization.name,
                    org_type=body.organization.type,
                    inputs=inputs_dict,
                    output=cleaned,
                    recommended_products=candidates,
                    historical_financials=credit_score,
                    model=f"{provider_used}/{model_used}",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
                db.add(rec)
                db.commit()
                db.refresh(rec)
                plan_id = rec.id

            yield _sse({"phase": "done", "pct": 100, "id": plan_id})

        except Exception as e:
            log.exception("Streamed business plan generation failed")
            msg = str(e)[:200] or "Unknown error"
            yield _sse({"phase": "error", "code": "internal", "message": msg})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            # Disable proxy buffering so events flush immediately.
            # Cloudflare and nginx both honor this header.
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.get("/{plan_id}/docx")
def download_plan_docx(plan_id: str, db: Session = Depends(get_db)):
    """Stream a .docx of the saved plan. Auth-free for now (the link
    contains an opaque UUID; if you need stricter access, mirror the
    `_require_user` dep used on /generate). The frontend uses fetch with
    the bearer token, so toggling auth on later is a one-line change."""
    rec = db.get(BusinessPlanSubmission, plan_id)
    if not rec or rec.error or not rec.output:
        raise HTTPException(status_code=404, detail="Business plan not found")

    blob = docx_builder.build_docx(
        plan=rec.output,
        inputs=rec.inputs or {},
        credit_score=rec.historical_financials,
        lang=(rec.lang or "ru"),
    )

    safe_name = (rec.org_name or "business-plan")
    safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in safe_name)[:60]
    filename = f"{safe_name or 'business-plan'}_{rec.id[:8]}.docx"

    return Response(
        content=blob,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{plan_id}")
def get_plan(plan_id: str, db: Session = Depends(get_db)):
    """Fetch a saved business plan. Used by the result page on refresh."""
    rec = db.get(BusinessPlanSubmission, plan_id)
    if not rec or rec.error:
        raise HTTPException(status_code=404, detail="Business plan not found")
    return {
        "id": rec.id,
        "createdAt": rec.created_at.isoformat(),
        "lang": rec.lang,
        "inputs": rec.inputs,
        "output": rec.output,
        "recommendedProductsCandidates": rec.recommended_products,
        "creditScore": rec.historical_financials,  # column re-purposed; see generate()
    }


@router.post("/parse-excel")
async def parse_excel(
    balance: UploadFile = File(..., description="Form №1 — Бухгалтерский баланс (.xlsx)"),
    pnl: UploadFile = File(..., description="Form №2 — Отчёт о финансовых результатах (.xlsx)"),
    auth_payload: dict = Depends(_require_user),
):
    """Parse the standard Uzbek SME tax forms (Form №1 + Form №2) and
    return extracted figures + computed credit-scoring ratios + verdict.

    Stateless — does NOT save to DB. The frontend keeps the result and
    posts it back as `historicalFinancials` in the /generate request when
    the user submits the full plan.
    """
    if not balance.filename.endswith(".xlsx") or not pnl.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Both files must be .xlsx")

    balance_bytes = await balance.read()
    pnl_bytes = await pnl.read()

    if not balance_bytes or not pnl_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    try:
        balance_data = excel_parser_msb.parse_balance(balance_bytes)
    except Exception as e:
        log.exception("Failed to parse balance sheet")
        raise HTTPException(status_code=400, detail=f"Не удалось разобрать баланс (Форма №1): {e}")

    try:
        pnl_data = excel_parser_msb.parse_pnl(pnl_bytes)
    except Exception as e:
        log.exception("Failed to parse P&L")
        raise HTTPException(status_code=400, detail=f"Не удалось разобрать отчёт о фин. результатах (Форма №2): {e}")

    # NO scoring at this stage — scoring runs at /generate time when we
    # have the project parameters too. Step 0 only confirms parse success
    # and shows the user a small preview of extracted figures.
    balance = {k: v for k, v in balance_data.items() if not k.startswith("_")}
    pnl = {k: v for k, v in pnl_data.items() if not k.startswith("_")}

    return {
        "balance": balance,
        "pnl": pnl,
        "summary": {
            "revenue": pnl.get("revenue", 0),
            "netProfit": pnl.get("netProfit", 0),
            "totalAssets": balance.get("totalAssets", 0),
            "equity": balance.get("equity", 0),
            "totalLiabilities": balance.get("totalLiabilities", 0),
        },
    }


# ---------- admin ----------

admin_router = APIRouter(prefix="/admin/business-plans", tags=["business-plan-admin"])


@admin_router.get("", response_model=list[AdminListItem])
def admin_list(
    db: Session = Depends(get_db),
    _admin: dict = Depends(_require_admin),
    limit: int = 100,
):
    rows = (
        db.query(BusinessPlanSubmission)
        .order_by(BusinessPlanSubmission.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        AdminListItem(
            id=r.id,
            createdAt=r.created_at.isoformat(),
            userEmail=r.user_email,
            lang=r.lang,
            orgName=r.org_name,
            orgType=r.org_type,
            inputTokens=r.input_tokens,
            outputTokens=r.output_tokens,
            hasError=bool(r.error),
        )
        for r in rows
    ]


@admin_router.get("/{plan_id}")
def admin_detail(
    plan_id: str,
    db: Session = Depends(get_db),
    _admin: dict = Depends(_require_admin),
):
    rec = db.get(BusinessPlanSubmission, plan_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {
        "id": rec.id,
        "createdAt": rec.created_at.isoformat(),
        "userEmail": rec.user_email,
        "lang": rec.lang,
        "orgName": rec.org_name,
        "orgType": rec.org_type,
        "inputs": rec.inputs,
        "output": rec.output,
        "recommendedProductsCandidates": rec.recommended_products,
        "creditScore": rec.historical_financials,
        "model": rec.model,
        "inputTokens": rec.input_tokens,
        "outputTokens": rec.output_tokens,
        "error": rec.error,
    }
