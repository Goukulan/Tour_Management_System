from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_guide
from app.models.users import User
from app.schemas.guide_operations import (
    GuideDepartureOut, TravelerRosterItem, CheckInRequest, AttendanceOut,
)
from app.services import guide_operations_service

router = APIRouter(prefix="/api/v1/guide/departures", tags=["Guide - Departures"])


def _to_out(d) -> GuideDepartureOut:
    return GuideDepartureOut(
        public_id=d.public_id,
        tour_title=d.tour.title,
        start_date=d.start_date,
        end_date=d.end_date,
        total_slots=d.total_slots,
        slots_booked=d.slots_booked,
        status=d.status.value,
        actual_start_at=d.actual_start_at,
        actual_end_at=d.actual_end_at,
    )


@router.get("", response_model=List[GuideDepartureOut])
def list_my_departures(db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    departures = guide_operations_service.list_my_departures(db, guide)
    return [_to_out(d) for d in departures]


@router.get("/{public_id}", response_model=GuideDepartureOut)
def get_departure(public_id: str, db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    return _to_out(guide_operations_service.get_departure_detail(db, guide, public_id))


@router.get("/{public_id}/roster", response_model=List[TravelerRosterItem])
def get_roster(public_id: str, db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    return guide_operations_service.get_tourist_roster(db, guide, public_id)


@router.post("/{public_id}/start", response_model=GuideDepartureOut)
def start_tour(public_id: str, db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    return _to_out(guide_operations_service.start_tour(db, guide, public_id))


@router.post("/{public_id}/end", response_model=GuideDepartureOut)
def end_tour(public_id: str, db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    return _to_out(guide_operations_service.end_tour(db, guide, public_id))


@router.post("/{public_id}/check-in", response_model=AttendanceOut)
def check_in(
    public_id: str, payload: CheckInRequest,
    db: Session = Depends(get_db), guide: User = Depends(get_current_guide),
):
    record = guide_operations_service.check_in_traveler(db, guide, public_id, payload)
    return AttendanceOut(
        traveler_public_id=record.traveler.public_id,
        traveler_name=record.traveler.full_name,
        present=record.present,
        checked_in_at=record.checked_in_at,
    )


@router.get("/{public_id}/attendance", response_model=List[AttendanceOut])
def get_attendance(public_id: str, db: Session = Depends(get_db), guide: User = Depends(get_current_guide)):
    records = guide_operations_service.list_attendance(db, guide, public_id)
    return [
        AttendanceOut(
            traveler_public_id=r.traveler.public_id,
            traveler_name=r.traveler.full_name,
            present=r.present,
            checked_in_at=r.checked_in_at,
        )
        for r in records
    ]