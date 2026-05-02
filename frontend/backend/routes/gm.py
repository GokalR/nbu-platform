"""Golden Mart API — read schema + entities, read/write data rows.

Phase B endpoints:
  GET  /api/gm/schema/{level}             — sections + fields for a level
  GET  /api/gm/entities                   — list entities (optional ?level=)
  GET  /api/gm/data/{level}/{key}         — full data, all years × all fields
  GET  /api/gm/data/{level}/{key}/{year}  — single-year row
  PUT  /api/gm/data/{level}/{key}/{year}  — admin write (auth: admin role)
  GET  /api/gm/coverage/{level}/{key}     — filled/total per section

Field columns are positional (s{section}_{index}). The frontend joins
schema + values at render time. Backend doesn't try to be clever with
labels — that lives in citySchema.js / regionSchema.js / countrySchema.js.
"""
from __future__ import annotations
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import require_auth, get_db
from models import User
import gm_models as gm

router = APIRouter(prefix="/api/gm", tags=["gm"])


LEVEL_TO_MODEL = {
    "country": gm.GmCountry,
    "region":  gm.GmRegion,
    "city":    gm.GmCity,
}


def _model_for(level: str):
    if level not in LEVEL_TO_MODEL:
        raise HTTPException(status_code=400, detail=f"Unknown level: {level}")
    return LEVEL_TO_MODEL[level]


def _row_to_dict(row, model) -> dict[str, Any]:
    """Turn a SQLAlchemy row into a plain dict, decimals → floats."""
    d = {}
    for col in model.__table__.columns:
        v = getattr(row, col.name, None)
        if v is None:
            d[col.name] = None
        elif col.type.python_type in (int, str, bool):
            d[col.name] = v
        else:
            try:
                d[col.name] = float(v)
            except (TypeError, ValueError):
                d[col.name] = str(v)
    return d


def _gm_field_keys(model) -> list[str]:
    """All s{n}_{i} field columns on a model (excludes meta)."""
    meta = {"entity_key", "year", "region_key", "updated_at", "updated_by"}
    return [c.name for c in model.__table__.columns if c.name not in meta]


def _require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")


# ─────────────────────────────────────────────────────────────────────
# GET /api/gm/entities
# ─────────────────────────────────────────────────────────────────────
@router.get("/entities")
async def list_entities(
    level: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(gm.GmEntity).where(gm.GmEntity.active.is_(True))
    if level:
        stmt = stmt.where(gm.GmEntity.level == level)
    stmt = stmt.order_by(gm.GmEntity.level, gm.GmEntity.key)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "key": r.key,
            "level": r.level,
            "parent_key": r.parent_key,
            "name_ru": r.name_ru,
            "name_uz": r.name_uz,
            "iso_kind": r.iso_kind,
        }
        for r in rows
    ]


# ─────────────────────────────────────────────────────────────────────
# GET /api/gm/data/{level}/{key} — all years
# GET /api/gm/data/{level}/{key}/{year}
# ─────────────────────────────────────────────────────────────────────
@router.get("/data/{level}/{key}")
async def get_entity_data(
    level: str,
    key: str,
    db: AsyncSession = Depends(get_db),
):
    model = _model_for(level)
    stmt = select(model).where(model.entity_key == key).order_by(model.year)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return {
        "level": level,
        "entity_key": key,
        "rows": [_row_to_dict(r, model) for r in rows],
    }


@router.get("/data/{level}/{key}/{year}")
async def get_entity_year(
    level: str,
    key: str,
    year: int,
    db: AsyncSession = Depends(get_db),
):
    model = _model_for(level)
    stmt = select(model).where(model.entity_key == key, model.year == year)
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if not row:
        # Return null fields for an empty cell instead of 404 — admin form
        # can still render the empty inputs and submit a fresh row.
        return {
            "level": level,
            "entity_key": key,
            "year": year,
            "exists": False,
            "values": {k: None for k in _gm_field_keys(model)},
        }
    return {
        "level": level,
        "entity_key": key,
        "year": year,
        "exists": True,
        "values": _row_to_dict(row, model),
    }


# ─────────────────────────────────────────────────────────────────────
# PUT /api/gm/data/{level}/{key}/{year}
# Body: { "values": { "s1_1": "Qoʻqon", "s2_2": 9410.4, ... } }
# Only admin role can write.
# ─────────────────────────────────────────────────────────────────────
class WriteBody(BaseModel):
    values: dict[str, Any]


@router.put("/data/{level}/{key}/{year}")
async def write_entity_year(
    level: str,
    key: str,
    year: int,
    body: WriteBody,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    _require_admin(user)
    model = _model_for(level)
    valid_fields = set(_gm_field_keys(model))

    payload = {k: v for k, v in body.values.items() if k in valid_fields}
    payload["updated_by"] = user.id

    # Upsert via merge: select + update or insert
    stmt = select(model).where(model.entity_key == key, model.year == year)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is None:
        new_kwargs = {"entity_key": key, "year": year, **payload}
        # Fill region_key for cities
        if level == "city":
            ent = await db.execute(
                select(gm.GmEntity).where(gm.GmEntity.key == key)
            )
            entity = ent.scalar_one_or_none()
            if entity:
                new_kwargs["region_key"] = entity.parent_key
        db.add(model(**new_kwargs))
    else:
        for k_, v_ in payload.items():
            setattr(existing, k_, v_)

    await db.commit()
    return {"ok": True, "updated_fields": list(payload.keys())}


# ─────────────────────────────────────────────────────────────────────
# GET /api/gm/coverage/{level}/{key} — fill stats per year and overall
# ─────────────────────────────────────────────────────────────────────
@router.get("/coverage/{level}/{key}")
async def coverage(
    level: str,
    key: str,
    db: AsyncSession = Depends(get_db),
):
    model = _model_for(level)
    field_keys = _gm_field_keys(model)
    total_per_row = len(field_keys)

    stmt = select(model).where(model.entity_key == key).order_by(model.year)
    rows = (await db.execute(stmt)).scalars().all()

    per_year = []
    overall_filled = 0
    for r in rows:
        d = _row_to_dict(r, model)
        filled = sum(
            1 for k in field_keys if d.get(k) not in (None, "")
        )
        overall_filled += filled
        per_year.append({"year": r.year, "filled": filled, "total": total_per_row})

    overall_total = total_per_row * len(rows) if rows else 0
    return {
        "level": level,
        "entity_key": key,
        "per_year": per_year,
        "overall": {
            "filled": overall_filled,
            "total": overall_total,
            "pct": round(100 * overall_filled / overall_total, 1) if overall_total else 0,
        },
    }
