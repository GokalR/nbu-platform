"""Routes for SME Business Plan generation + admin review."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db_sync import get_db
from ..models_business_plan import BusinessPlanSubmission
from ..services import business_plan_client, credit_scoring, excel_parser_msb, nbu_products

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
    # Optional historical financials parsed from Form №1 + Form №2 in Step 0.
    # Frontend posts back exactly what /parse-excel returned.
    historicalFinancials: dict[str, Any] | None = None


class GenerateResponse(BaseModel):
    id: str
    output: dict[str, Any]
    recommendedProductsCandidates: list[dict[str, Any]]


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

    # Pre-compute deterministic baseline so we can use it both for credit
    # scoring (below) and pass it to the LLM (avoid double-computation).
    from ..services import business_plan_compute as bpc
    baseline = bpc.compute_baseline(inputs_dict)

    # If user uploaded financials at Step 0, run combined scoring NOW
    # (Excel ratios + project-vs-history ratios — DSCR, loan/revenue,
    # equity-in-project) and attach to the historicalFinancials object.
    historical_financials = body.historicalFinancials
    if historical_financials and historical_financials.get("balance"):
        score = credit_scoring.compute_score(
            historical_financials.get("balance") or {},
            historical_financials.get("pnl") or {},
            baseline=baseline,
            inputs=inputs_dict,
        )
        # Mutate-in-place so the saved row + LLM prompt both have the score.
        historical_financials = {**historical_financials, "score": score}

    rec = BusinessPlanSubmission(
        user_email=user_email,
        lang=body.lang or "uz",
        org_name=body.organization.name,
        org_type=body.organization.type,
        inputs=inputs_dict,
        recommended_products=candidates,
        historical_financials=historical_financials,
        model="",
    )

    try:
        result = business_plan_client.generate_business_plan(
            inputs=inputs_dict,
            candidate_products=candidates,
            lang=body.lang or "uz",
            historical_financials=historical_financials,
            baseline=baseline,
        )
        rec.output = result["output"]
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
        "historicalFinancials": rec.historical_financials,
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
        "historicalFinancials": rec.historical_financials,
        "model": rec.model,
        "inputTokens": rec.input_tokens,
        "outputTokens": rec.output_tokens,
        "error": rec.error,
    }
