"""Precompute country aggregate JSON for the CERR v2 country page.

Replaces the live `/api/cerr/country/rankings` aggregation (which walks ~200
mahallas.json files from R2 on every cold start, ~20s) with a static file
served in ~10ms. Includes everything the country page needs in ONE response:

    - 14 regions with population, district/mahalla counts, rank, score
    - country-wide totals
    - tier counts (lead / mid / low) for the legend

Usage (local FS only — script reads CERR_DATA_ROOT directly):

    cd bff_frontend/backend
    python -m scripts.precompute_country_aggregate

Output: bff_frontend/backend/data/cerr_static/country_aggregate.json

Re-run whenever the underlying CERR JSON tree changes; commit the result.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

# Allow `python -m scripts.precompute_country_aggregate` from the backend dir.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
from app.services.cerr_data import CerrDataIndex  # noqa: E402


def _region_population(idx: CerrDataIndex, region_code: int) -> int | None:
    """Read population KPI from region.json overview.kpis[]."""
    ov = idx.get_region_overview(region_code) or {}
    for k in ov.get("kpis") or []:
        if k.get("key") == "population" and isinstance(k.get("value"), (int, float)):
            return int(k["value"])
    return None


def _tier_for_ratio(ratio: float) -> str:
    """Country-level uses 40/40/20 split (lead/mid/low)."""
    if ratio <= 0.40:
        return "lead"
    if ratio <= 0.80:
        return "mid"
    return "low"


def build_stir_index(idx: CerrDataIndex) -> dict[str, int]:
    """Walk every district's mahallas.json once and produce {stir: district_code}.
    Lets the backend answer mahalla-by-STIR lookups in 1 R2 fetch instead of
    walking up to 212 districts to find the owning file."""
    out: dict[str, int] = {}
    for d_code, d_meta in idx.districts.items():
        data = idx._reader.read_json(f"{d_meta['rel_dir']}/mahallas.json")
        if not data:
            continue
        for m in data.get("mahallas", []) or []:
            stir = str(m.get("stir") or "")
            if stir:
                out[stir] = d_code
    return out


def build_aggregate(idx: CerrDataIndex) -> dict:
    rankings = idx.get_country_rankings()
    rank_by_code = {r["code"]: r for r in rankings}

    region_rows: list[dict] = []
    total_pop = 0
    total_districts = 0
    total_mahallas = 0
    tier_counts = {"lead": 0, "mid": 0, "low": 0}
    total_ranked = len(rankings) or 1

    for r in idx.list_regions():
        code = r["code"]
        ranked = rank_by_code.get(code)
        pop = _region_population(idx, code) or 0
        total_pop += pop
        total_districts += r.get("districts_count", 0) or 0
        total_mahallas += r.get("mahalla_count", 0) or 0
        row = {
            "code": code,
            "name": r["name"],
            "districts_count": r.get("districts_count"),
            "mahalla_count": r.get("mahalla_count"),
            "population": pop,
            "rank": ranked["rank"] if ranked else None,
            "score": ranked["score"] if ranked else None,
            "has_cerr": ranked is not None,
        }
        if ranked:
            tier = _tier_for_ratio(ranked["rank"] / total_ranked)
            row["tier"] = tier
            tier_counts[tier] += 1
        region_rows.append(row)

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "regions": region_rows,
        "totals": {
            "population": total_pop,
            "districts": total_districts,
            "mahallas": total_mahallas,
            "regions": len(region_rows),
            "regions_with_data": sum(1 for r in region_rows if r["has_cerr"]),
        },
        "tier_counts": tier_counts,
    }


def main() -> int:
    settings = get_settings()
    root = settings.cerr_data_root_resolved
    print(f"CERR_DATA_ROOT: {root}")
    if root.startswith("http"):
        print("ERROR: precompute must run against a local FS root, not R2.", file=sys.stderr)
        return 1

    idx = CerrDataIndex(root)
    print("Building country aggregate (walks all districts and their mahallas.json)...")
    aggregate = build_aggregate(idx)
    # Reuses the reader's cache populated by get_country_rankings, so no extra IO.
    print("Building STIR -> district_code index...")
    stir_index = build_stir_index(idx)

    out_dir = ROOT / "data" / "cerr_static"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_agg = out_dir / "country_aggregate.json"
    out_agg.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
    out_idx = out_dir / "mahalla_stir_index.json"
    # Compact (no indent) — file is large-ish (~200 KB) and never read by humans.
    out_idx.write_text(json.dumps(stir_index, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    print(f"Wrote {out_agg} ({out_agg.stat().st_size / 1024:.1f} KB)")
    print(f"Wrote {out_idx} ({out_idx.stat().st_size / 1024:.1f} KB, {len(stir_index)} entries)")
    print(f"  regions:           {len(aggregate['regions'])}")
    print(f"  with_data:         {aggregate['totals']['regions_with_data']}")
    print(f"  total population:  {aggregate['totals']['population']:,}")
    print(f"  total districts:   {aggregate['totals']['districts']}")
    print(f"  total mahallas:    {aggregate['totals']['mahallas']}")
    print(f"  tier counts:       {aggregate['tier_counts']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
