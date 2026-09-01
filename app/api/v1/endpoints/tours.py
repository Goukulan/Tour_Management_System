from typing import List, Optional
from decimal import Decimal
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.public import PublicTourListItem, PublicTourDetailOut, PublicDepartureOut
from app.services import tour_service, departure_service

router = APIRouter(prefix="/api/v1/tours", tags=["Public - Tours"])


@router.get("", response_model=List[PublicTourListItem])
def search_tours(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    destination_public_id: Optional[str] = Query(None),
    category_public_id: Optional[str] = Query(None),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    min_duration_days: Optional[int] = Query(None, ge=1),
    max_duration_days: Optional[int] = Query(None, ge=1),
    keyword: Optional[str] = Query(None, description="Search by tour title"),
    db: Session = Depends(get_db),
):
    return tour_service.search_public_tours(
        db,
        skip=skip,
        limit=limit,
        destination_public_id=destination_public_id,
        category_public_id=category_public_id,
        min_price=min_price,
        max_price=max_price,
        min_duration_days=min_duration_days,
        max_duration_days=max_duration_days,
        keyword=keyword,
    )


@router.get("/{slug}", response_model=PublicTourDetailOut)
def get_tour(slug: str, db: Session = Depends(get_db)):
    return tour_service.get_public_tour_by_slug(db, slug)


@router.get("/{slug}/departures", response_model=List[PublicDepartureOut])
def list_tour_departures(
    slug: str,
    from_date: Optional[date] = Query(None, description="Defaults to today"),
    db: Session = Depends(get_db),
):
    return departure_service.list_public_departures_for_tour(db, slug, from_date=from_date)