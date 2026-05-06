"""Read-only API for CERR Mahalla Analytics v2.

Mounted at /api/cerr. Backed entirely by the file tree at CERR_DATA_ROOT
(see config.py). No DB, no auth — public within the platform's existing
auth wrapper, since the data is reference / open.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..services.cerr_data import get_cerr_index

router = APIRouter(prefix="/api/cerr", tags=["cerr-analytics"])


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
