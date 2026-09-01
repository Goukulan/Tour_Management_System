from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.departure import Departure
from app.models.tour import Tour
from app.schemas.departure import DepartureCreate, DepartureUpdate
from app.models.departure import DepartureStatusEnum



def _get_tour_or_404(db: Session, tour_public_id: str) -> Tour:
    tour = db.query(Tour).filter(Tour.public_id == tour_public_id).first()
    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found",
        )
    return tour


def create_departure(db: Session, tour_public_id: str, payload: DepartureCreate) -> Departure:
    tour = _get_tour_or_404(db, tour_public_id)

    departure = Departure(
        tour_id=tour.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_slots=payload.total_slots,
        price_override_adult=payload.price_override_adult,
        price_override_child=payload.price_override_child,
    )
    db.add(departure)
    db.commit()
    db.refresh(departure)
    return departure


def get_departure_by_public_id(db: Session, public_id: str) -> Departure:
    departure = (
        db.query(Departure)
        .options(joinedload(Departure.tour))
        .filter(Departure.public_id == public_id)
        .first()
    )
    if not departure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Departure not found",
        )
    return departure


def list_departures_for_tour(db: Session, tour_public_id: str, skip: int = 0, limit: int = 20):
    tour = _get_tour_or_404(db, tour_public_id)
    return (
        db.query(Departure)
        .filter(Departure.tour_id == tour.id)
        .order_by(Departure.start_date)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_departure(db: Session, public_id: str, payload: DepartureUpdate) -> Departure:
    departure = get_departure_by_public_id(db, public_id)

    update_data = payload.model_dump(exclude_unset=True)

    new_total_slots = update_data.get("total_slots")
    if new_total_slots is not None and new_total_slots < departure.slots_booked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set total_slots below already booked slots ({departure.slots_booked})",
        )

    for field, value in update_data.items():
        setattr(departure, field, value)

    db.commit()
    db.refresh(departure)
    return departure


def cancel_departure(db: Session, public_id: str) -> Departure:
    """Soft action, not a hard delete — see note below."""
    departure = get_departure_by_public_id(db, public_id)

    if departure.status == DepartureStatusEnum.cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departure is already cancelled",
        )

    departure.status = DepartureStatusEnum.cancelled
    db.commit()
    db.refresh(departure)

    # TODO once booking module exists:
    # - fetch all confirmed bookings for this departure
    # - trigger refund workflow (Celery task)
    # - notify affected travelers

    return departure


def delete_departure(db: Session, public_id: str) -> None:
    """True hard delete — only allowed if zero bookings exist."""
    departure = get_departure_by_public_id(db, public_id)

    if departure.slots_booked > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a departure with existing bookings. Cancel it instead.",
        )

    db.delete(departure)
    db.commit()



def list_public_departures_for_tour(db: Session, tour_slug: str, from_date: date | None = None):
    tour = db.query(Tour).filter(Tour.slug == tour_slug, Tour.is_active == True).first()
    if not tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")

    query = db.query(Departure).filter(
        Departure.tour_id == tour.id,
        Departure.status == DepartureStatusEnum.open,
    )

    if from_date:
        query = query.filter(Departure.start_date >= from_date)
    else:
        query = query.filter(Departure.start_date >= date.today())

    return query.order_by(Departure.start_date).all()