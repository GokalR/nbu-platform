"""Loads peer_benchmarks.json and exposes a comparison helper."""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "peer_benchmarks.json"


@lru_cache(maxsize=1)
def load() -> dict:
    if not _DATA.exists():
        return {"benchmarks": {}, "companies": [], "note": "peer_benchmarks.json not found"}
    with _DATA.open(encoding="utf-8") as fh:
        return json.load(fh)


def compare(user_ratios: dict[str, float | None]) -> list[dict]:
    bm = load().get("benchmarks", {})
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
