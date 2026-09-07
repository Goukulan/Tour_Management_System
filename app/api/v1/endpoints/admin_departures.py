from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.schemas.departure import DepartureCreate, DepartureUpdate, DepartureOut
from app.services import departure_service

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin - Departures"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("/tours/{tour_public_id}/departures", response_model=DepartureOut, status_code=status.HTTP_201_CREATED)
def create_departure(tour_public_id: str, payload: DepartureCreate, db: Session = Depends(get_db)):
    return departure_service.create_departure(db, tour_public_id, payload)


@router.get("/tours/{tour_public_id}/departures", response_model=List[DepartureOut])
def list_departures(
    tour_public_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return departure_service.list_departures_for_tour(db, tour_public_id, skip=skip, limit=limit)


@router.get("/departures/{public_id}", response_model=DepartureOut)
def get_departure(public_id: str, db: Session = Depends(get_db)):
    return departure_service.get_departure_by_public_id(db, public_id)


@router.patch("/departures/{public_id}", response_model=DepartureOut)
def update_departure(public_id: str, payload: DepartureUpdate, db: Session = Depends(get_db)):
    return departure_service.update_departure(db, public_id, payload)


@router.post("/departures/{public_id}/cancel", response_model=DepartureOut)
def cancel_departure(public_id: str, db: Session = Depends(get_db)):
    return departure_service.cancel_departure(db, public_id)


@router.delete("/departures/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_departure(public_id: str, db: Session = Depends(get_db)):
    departure_service.delete_departure(db, public_id)
    return None