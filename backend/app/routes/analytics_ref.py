"""Read-only endpoints for analytics reference data (regions, region_data)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_analytics_ref import Region, RegionData
from ..schemas import RegionDataOut, RegionListItem

router = APIRouter(prefix="/api/analytics", tags=["analytics-reference"])


@router.get("/regions", response_model=list[RegionListItem])
def list_regions(level: str | None = None, parent_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Region)
    if level:
        q = q.filter(Region.level == level)
    if parent_id:
        q = q.filter(Region.parent_id == parent_id)
    return q.order_by(Region.level, Region.name_ru).all()


@router.get("/regions/{region_id}", response_model=RegionListItem)
def get_region(region_id: str, db: Session = Depends(get_db)):
    row = db.get(Region, region_id)
    if not row:
        raise HTTPException(404, f"Region '{region_id}' not found")
    return row


@router.get("/regions/{region_id}/data", response_model=RegionDataOut)
def get_region_data(region_id: str, year: int = 2025, db: Session = Depends(get_db)):
    row = db.query(RegionData).filter_by(region_id=region_id, data_year=year).first()
    if not row:
        raise HTTPException(404, f"No data for region '{region_id}' year {year}")
    return row
