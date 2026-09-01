from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.schemas.tour import TourCreate, TourUpdate, TourOut
from app.schemas.tour_itinerary_day import ItineraryDayCreate, ItineraryDayUpdate, ItineraryDayOut
from app.services import tour_service

router = APIRouter(
    prefix="/api/v1/admin/tours",
    tags=["Admin - Tours"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=TourOut, status_code=status.HTTP_201_CREATED)
def create_tour(payload: TourCreate, db: Session = Depends(get_db)):
    return tour_service.create_tour(db, payload)


@router.get("", response_model=List[TourOut])
def list_tours(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_active: bool = Query(False),
    destination_public_id: Optional[str] = Query(None),
    category_public_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return tour_service.list_tours(
        db,
        skip=skip,
        limit=limit,
        only_active=only_active,
        destination_public_id=destination_public_id,
        category_public_id=category_public_id,
    )


@router.get("/{public_id}", response_model=TourOut)
def get_tour(public_id: str, db: Session = Depends(get_db)):
    return tour_service.get_tour_by_public_id(db, public_id)


@router.patch("/{public_id}", response_model=TourOut)
def update_tour(public_id: str, payload: TourUpdate, db: Session = Depends(get_db)):
    return tour_service.update_tour(db, public_id, payload)


@router.delete("/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tour(public_id: str, db: Session = Depends(get_db)):
    tour_service.delete_tour(db, public_id)
    return None


# ---------- Itinerary Day sub-routes (nested under a tour) ----------

@router.post("/{public_id}/itinerary-days", response_model=ItineraryDayOut, status_code=status.HTTP_201_CREATED)
def add_itinerary_day(public_id: str, payload: ItineraryDayCreate, db: Session = Depends(get_db)):
    return tour_service.add_itinerary_day(db, public_id, payload)


@router.patch("/{public_id}/itinerary-days/{day_number}", response_model=ItineraryDayOut)
def update_itinerary_day(
    public_id: str, day_number: int, payload: ItineraryDayUpdate, db: Session = Depends(get_db)
):
    return tour_service.update_itinerary_day(db, public_id, day_number, payload)


@router.delete("/{public_id}/itinerary-days/{day_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_itinerary_day(public_id: str, day_number: int, db: Session = Depends(get_db)):
    tour_service.delete_itinerary_day(db, public_id, day_number)
    return None