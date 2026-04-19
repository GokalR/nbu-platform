"""Loads peer benchmarks and exposes a comparison helper.

Reads from DB first (peer_benchmarks table), falls back to peer_benchmarks.json.
"""
from __future__ import annotations
import json
import logging
from functools import lru_cache
from pathlib import Path

from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "peer_benchmarks.json"


@lru_cache(maxsize=1)
def _load_from_file() -> dict:
    if not _DATA.exists():
        return {"benchmarks": {}, "companies": [], "note": "peer_benchmarks.json not found"}
    with _DATA.open(encoding="utf-8") as fh:
        return json.load(fh)


def load(db: Session | None = None, region: str = "fergana") -> dict:
    if db is not None:
        try:
            from ..models_rs_ref import PeerBenchmarkSet
            row = db.query(PeerBenchmarkSet).filter_by(region=region).first()
            if row:
                return {"benchmarks": row.benchmarks, "companies": row.companies}
        except Exception as e:
            log.warning("DB benchmark lookup failed: %s", e)
    return _load_from_file()


def compare(user_ratios: dict[str, float | None], db: Session | None = None) -> list[dict]:
    bm = load(db=db).get("benchmarks", {})
    out = []
    for key, row in bm.items():
        user = user_ratios.get(key)
        median = row.get("median")
        q1, q3 = row.get("q1"), row.get("q3")
        hint = None
        if user is not None and median is not None:
            if q3 is not None and user >= q3:
                hint = "top"
            elif q1 is not None and user <= q1:
                hint = "bottom"
            else:
                hint = "middle"
        out.append({
            "key": key,
            "user": user,
            "q1": q1,
            "median": median,
            "q3": q3,
            "n": row.get("n"),
            "percentileHint": hint,
        })
    return out
