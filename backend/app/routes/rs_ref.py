"""Read-only endpoints for Regional Strategist reference data (cities, benchmarks)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_rs_ref import City, PeerBenchmarkSet
from ..schemas import BenchmarkSetOut, CityListItem, CityOut

router = APIRouter(prefix="/reference", tags=["rs-reference"])


@router.get("/cities", response_model=list[CityListItem])
def list_cities(db: Session = Depends(get_db)):
    return db.query(City).order_by(City.level, City.name_ru).all()


@router.get("/cities/{city_id}", response_model=CityOut)
def get_city(city_id: str, db: Session = Depends(get_db)):
    row = db.get(City, city_id)
    if not row:
        raise HTTPException(404, f"City '{city_id}' not found")
    return row


@router.get("/benchmarks/{region}", response_model=BenchmarkSetOut)
def get_benchmarks(region: str, db: Session = Depends(get_db)):
    row = db.query(PeerBenchmarkSet).filter_by(region=region).first()
    if not row:
        raise HTTPException(404, f"No benchmarks for region '{region}'")
    return row
