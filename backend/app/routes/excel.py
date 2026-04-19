from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db_sync import get_db
from ..models_analytics import ExcelUpload, Submission
from ..schemas import UploadOut
from ..services import excel_parser

import logging
log = logging.getLogger(__name__)

router = APIRouter(prefix="/submissions/{sub_id}/uploads", tags=["excel"])


@router.post("", response_model=UploadOut, status_code=status.HTTP_201_CREATED)
async def upload_excel(
    sub_id: str,
    kind: str = Form(..., description="'balance' or 'pnl'"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if kind not in ("balance", "pnl"):
        raise HTTPException(400, "kind must be 'balance' or 'pnl'")

    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")

    settings = get_settings()
    blob = await file.read()
    if len(blob) > settings.max_upload_bytes:
        raise HTTPException(413, f"File too large (>{settings.max_upload_bytes} bytes)")

    try:
        parsed = excel_parser.parse(kind, blob)
    except Exception as e:
        log.error("Excel parse error for submission %s: %s", sub_id, e)
        raise HTTPException(422, "Could not parse the uploaded Excel file. Please check the format.") from e

    # Claude returns { "codes": {...}, "computed": { "absolutes": {...}, "ratios": {...} } }
    # Rule-based fallback returns just codes dict — wrap it for compatibility
    if "computed" not in parsed:
        from ..services import ratios
        combined_form1 = parsed if kind == "balance" else None
        combined_form2 = parsed if kind == "pnl" else None
        for prev in sub.uploads:
            if prev.kind == "balance" and kind == "pnl":
                combined_form1 = prev.parsed.get("codes", {})
            elif prev.kind == "pnl" and kind == "balance":
                combined_form2 = prev.parsed.get("codes", {})
        computed = ratios.compute(combined_form1, combined_form2)
        parsed = {"codes": parsed, "computed": computed}

    rec = ExcelUpload(
        submission_id=sub_id,
        kind=kind,
        original_filename=file.filename or "upload.xlsx",
        size_bytes=len(blob),
        parsed=parsed,
        raw_blob=None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("", response_model=list[UploadOut])
def list_uploads(sub_id: str, db: Session = Depends(get_db)):
    sub = db.get(Submission, sub_id)
    if not sub:
        raise HTTPException(404, "Submission not found")
    return sub.uploads
