from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db_sync import get_db
from ..models_analytics import ExcelUpload, Submission
from ..schemas import UploadOut
from ..services import excel_parser, ratios

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
        parsed_codes = excel_parser.parse(kind, blob)
    except Exception as e:
        raise HTTPException(422, f"Could not parse Excel: {e}") from e

    combined_form1 = parsed_codes if kind == "balance" else None
    combined_form2 = parsed_codes if kind == "pnl" else None

    for prev in sub.uploads:
        if prev.kind == "balance" and kind == "pnl":
            combined_form1 = prev.parsed.get("codes", {})
        elif prev.kind == "pnl" and kind == "balance":
            combined_form2 = prev.parsed.get("codes", {})

    computed = ratios.compute(combined_form1, combined_form2)

    rec = ExcelUpload(
        submission_id=sub_id,
        kind=kind,
        original_filename=file.filename or "upload.xlsx",
        size_bytes=len(blob),
        parsed={"codes": parsed_codes, "computed": computed},
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
