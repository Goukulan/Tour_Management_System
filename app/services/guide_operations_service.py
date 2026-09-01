from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.departure import Departure
from app.models.guide_assignment import GuideAssignment
from app.models.booking import Booking
from app.models.booking_traveler import BookingTraveler
from app.models.attendance import Attendance
from app.models.users import User
from app.models.booking import BookingStatusEnum
from app.schemas.guide_operations import CheckInRequest


def _get_assigned_departure_or_403(db: Session, guide: User, departure_public_id: str) -> Departure:
    departure = (
        db.query(Departure)
        .options(joinedload(Departure.tour))
        .filter(Departure.public_id == departure_public_id)
        .first()
    )
    if not departure:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departure not found")

    assignment = (
        db.query(GuideAssignment)
        .filter(GuideAssignment.guide_id == guide.id, GuideAssignment.departure_id == departure.id)
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this departure",
        )

    return departure


def list_my_departures(db: Session, guide: User):
    return (
        db.query(Departure)
        .join(GuideAssignment, GuideAssignment.departure_id == Departure.id)
        .options(joinedload(Departure.tour))
        .filter(GuideAssignment.guide_id == guide.id)
        .order_by(Departure.start_date)
        .all()
    )


def get_departure_detail(db: Session, guide: User, departure_public_id: str) -> Departure:
    return _get_assigned_departure_or_403(db, guide, departure_public_id)


def get_tourist_roster(db: Session, guide: User, departure_public_id: str):
    departure = _get_assigned_departure_or_403(db, guide, departure_public_id)

    travelers = (
        db.query(BookingTraveler)
        .join(Booking, Booking.id == BookingTraveler.booking_id)
        .options(joinedload(BookingTraveler.booking).joinedload(Booking.user))
        .filter(Booking.departure_id == departure.id, Booking.status == BookingStatusEnum.confirmed)
        .all()
    )

    checked_in_ids = {
        a.booking_traveler_id
        for a in db.query(Attendance).filter(Attendance.departure_id == departure.id).all()
    }

    roster = []
    for t in travelers:
        roster.append({
            "public_id": t.public_id,
            "full_name": t.full_name,
            "age": t.age,
            "gender": t.gender,
            "booking_public_id": t.booking.public_id,
            "booker_name": t.booking.user.full_name,
            "booker_phone": t.booking.user.phone,
            "is_checked_in": t.id in checked_in_ids,
        })
    return roster


def start_tour(db: Session, guide: User, departure_public_id: str) -> Departure:
    departure = _get_assigned_departure_or_403(db, guide, departure_public_id)

    if departure.actual_start_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tour has already been started")

    departure.actual_start_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(departure)
    return departure


def end_tour(db: Session, guide: User, departure_public_id: str) -> Departure:
    departure = _get_assigned_departure_or_403(db, guide, departure_public_id)

    if departure.actual_start_at is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tour has not been started yet")
    if departure.actual_end_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tour has already been ended")

    departure.actual_end_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(departure)
    return departure


def check_in_traveler(db: Session, guide: User, departure_public_id: str, payload: CheckInRequest) -> Attendance:
    departure = _get_assigned_departure_or_403(db, guide, departure_public_id)

    traveler = (
        db.query(BookingTraveler)
        .join(Booking, Booking.id == BookingTraveler.booking_id)
        .filter(
            BookingTraveler.public_id == payload.traveler_public_id,
            Booking.departure_id == departure.id,
            Booking.status == BookingStatusEnum.confirmed,
        )
        .first()
    )
    if not traveler:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Traveler is not on this departure's confirmed roster",
        )

    record = (
        db.query(Attendance)
        .filter(Attendance.departure_id == departure.id, Attendance.booking_traveler_id == traveler.id)
        .first()
    )
    if record:
        record.present = payload.present
        record.marked_by_guide_id = guide.id
    else:
        record = Attendance(
            departure_id=departure.id,
            booking_traveler_id=traveler.id,
            present=payload.present,
            marked_by_guide_id=guide.id,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


def list_attendance(db: Session, guide: User, departure_public_id: str):
    departure = _get_assigned_departure_or_403(db, guide, departure_public_id)
    return (
        db.query(Attendance)
        .options(joinedload(Attendance.traveler))
        .filter(Attendance.departure_id == departure.id)
        .all()
    )