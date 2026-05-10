"""Read-only API for CERR Mahalla Analytics v2.

Mounted at /api/cerr. Backed entirely by the file tree at CERR_DATA_ROOT
(see config.py). No DB, no auth — public within the platform's existing
auth wrapper, since the data is reference / open.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from ..services.cerr_data import get_cerr_index

router = APIRouter(prefix="/api/cerr", tags=["cerr-analytics"])


# Static datasets shipped with the backend (geo polygons + RAQAMLARDA macro).
# bff_frontend/backend/app/routes/cerr.py -> parents[2] is bff_frontend/backend/.
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_GEO_DIR = _DATA_DIR / "geo"
_RAQAMLARDA_FILE = _DATA_DIR / "raqamlarda.json"


@lru_cache(maxsize=1)
def _geo_index() -> dict[int, str]:
    """region_code -> region_slug, from geo_json/index.json."""
    p = _GEO_DIR / "index.json"
    if not p.exists():
        return {}
    j = json.loads(p.read_text(encoding="utf-8"))
    return {int(r["region_code"]): r["region_slug"] for r in j.get("regions", [])}


@lru_cache(maxsize=1)
def _country_geo() -> dict | None:
    p = _GEO_DIR / "regions.geojson"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=14)
def _region_districts_geo(region_code: int) -> dict | None:
    slug = _geo_index().get(region_code)
    if not slug:
        return None
    p = _GEO_DIR / "regions" / slug / "districts.geojson"
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _raqamlarda() -> dict:
    if not _RAQAMLARDA_FILE.exists():
        return {}
    return json.loads(_RAQAMLARDA_FILE.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------
# Regions
# ----------------------------------------------------------------------

@router.get("/regions")
def list_regions():
    return get_cerr_index().list_regions()


@router.get("/regions/{region_code}")
def get_region(region_code: int):
    r = get_cerr_index().get_region(region_code)
    if r is None:
        raise HTTPException(404, f"Region {region_code} not found")
    return r


@router.get("/regions/{region_code}/overview")
def region_overview(region_code: int):
    ov = get_cerr_index().get_region_overview(region_code)
    if ov is None:
        raise HTTPException(404, f"Region {region_code} overview not found")
    return ov


@router.get("/regions/{region_code}/districts")
def region_districts(region_code: int):
    return get_cerr_index().list_region_districts(region_code)


# ----------------------------------------------------------------------
# Districts
# ----------------------------------------------------------------------

@router.get("/districts/{district_code}")
def get_district(district_code: int):
    d = get_cerr_index().get_district(district_code)
    if d is None:
        raise HTTPException(404, f"District {district_code} not found")
    return d


@router.get("/districts/{district_code}/overview")
def district_overview(district_code: int):
    ov = get_cerr_index().get_district_overview(district_code)
    if ov is None:
        raise HTTPException(404, f"District {district_code} overview not found")
    return ov


@router.get("/districts/{district_code}/macro")
def district_macro(district_code: int):
    macro = get_cerr_index().get_district_macro(district_code)
    if macro is None:
        raise HTTPException(404, f"District {district_code} macro not found")
    return macro


@router.get("/districts/{district_code}/mahallas")
def district_mahallas(
    district_code: int,
    sort: str = Query("rating_asc", pattern="^(rating_asc|rating_desc)$"),
    limit: int = Query(500, ge=1, le=2000),
):
    return get_cerr_index().list_district_mahallas(district_code, sort=sort, limit=limit)


@router.get("/districts/{district_code}/geo")
def district_geo(district_code: int):
    """GeoJSON FeatureCollection in WGS84 (lon/lat) — consumed directly by MapLibre."""
    fc = get_cerr_index().get_district_geo(district_code)
    if fc is None:
        raise HTTPException(404, f"District {district_code} geo not found")
    return fc


# ----------------------------------------------------------------------
# Mahallas
# ----------------------------------------------------------------------

@router.get("/mahallas/search")
def search_mahallas(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=500),
):
    return get_cerr_index().search_mahallas(q, limit=limit)


@router.get("/mahallas/{stir}")
def mahalla_overview(stir: str):
    ov = get_cerr_index().get_mahalla_overview(stir)
    if ov is None:
        raise HTTPException(404, f"Mahalla {stir} not found")
    return ov


@router.get("/mahallas/{stir}/ai_insights")
def mahalla_ai_insights(stir: str):
    ai = get_cerr_index().get_mahalla_ai_insights(stir)
    if ai is None:
        raise HTTPException(404, f"AI insights for mahalla {stir} not found")
    return ai


# ----------------------------------------------------------------------
# Geo (country regions, region districts) — for cerr-v2 choropleths.
# Mahalla-level GeoJSON stays at /districts/{code}/geo above.
# ----------------------------------------------------------------------

@router.get("/geo/country")
def country_geo():
    """14-region FeatureCollection (WGS84 lon/lat) for the country choropleth."""
    fc = _country_geo()
    if fc is None:
        raise HTTPException(404, "Country regions GeoJSON not found")
    return fc


@router.get("/regions/{region_code}/geo")
def region_districts_geo(region_code: int):
    """Per-region district FeatureCollection (WGS84 lon/lat). All 14 regions covered."""
    fc = _region_districts_geo(region_code)
    if fc is None:
        raise HTTPException(404, f"District GeoJSON for region {region_code} not found")
    return fc


# ----------------------------------------------------------------------
# RAQAMLARDA — national + per-region macro indicators (NOT in cerr_runs;
# compiled from REGIONS_RAQAMLARDA.md into bff_frontend/backend/data/raqamlarda.json).
# ----------------------------------------------------------------------

@router.get("/raqamlarda/{scope}")
def raqamlarda(scope: str):
    """scope ∈ "national" | "<region_code>" (e.g. "1703")."""
    data = _raqamlarda()
    if not data:
        raise HTTPException(404, "RAQAMLARDA dataset not loaded")
    rec = data.get(scope)
    if rec is None:
        raise HTTPException(404, f"RAQAMLARDA scope '{scope}' not found")
    return rec


# ----------------------------------------------------------------------
# Country-level region rankings — aggregates mahalla rating_score VALUE
# up the hierarchy (mahalla → district mean → region mean → ranked).
# This is the country-comparable composite score, distinct from the
# region-relative rating_score "place" rank stored per district/mahalla.
# ----------------------------------------------------------------------

@router.get("/country/rankings")
def country_rankings():
    """Returns the 14 regions ranked by mean of mean mahalla rating_score."""
    return get_cerr_index().get_country_rankings()
