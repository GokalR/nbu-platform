"""Read-only endpoints for Regional Strategist reference data."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db_sync import get_db
from ..models_rs_ref import (
    City,
    CityDistrict,
    CityEnterprise,
    CreditProduct,
    PeerBenchmarkSet,
)
from ..schemas import (
    BenchmarkSetOut,
    CityDistrictOut,
    CityEnterpriseOut,
    CityListItem,
    CityOut,
    CreditProductOut,
)

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


@router.get("/districts", response_model=list[CityDistrictOut])
def list_districts(
    city_id: str = Query(..., description="City id, e.g. 'fergana' or 'margilan'"),
    db: Session = Depends(get_db),
):
    return (
        db.query(CityDistrict)
        .filter(CityDistrict.city_id == city_id)
        .order_by(CityDistrict.sort_order, CityDistrict.name_ru)
        .all()
    )


@router.get("/enterprises", response_model=list[CityEnterpriseOut])
def list_enterprises(
    city_id: str = Query(...),
    sector: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(CityEnterprise).filter(CityEnterprise.city_id == city_id)
    if sector:
        q = q.filter(CityEnterprise.sector == sector)
    return q.order_by(CityEnterprise.name).all()


@router.get("/credit-products", response_model=list[CreditProductOut])
def list_credit_products(
    tier: Optional[str] = Query(None, description="Filter by 'easy' or 'standard'"),
    db: Session = Depends(get_db),
):
    q = db.query(CreditProduct)
    if tier:
        q = q.filter(CreditProduct.tier == tier)
    return q.order_by(CreditProduct.sort_order, CreditProduct.id).all()
