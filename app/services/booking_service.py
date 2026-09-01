import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.booking import Booking
from app.models.booking_traveler import BookingTraveler
from app.models.departure import Departure
from app.models.users import User
from app.models.booking import BookingStatusEnum
from app.models.departure import DepartureStatusEnum
from app.schemas.booking import BookingCreate
from app.core.redis_client import acquire_seat_hold, get_active_holds_count, release_seat_hold
from app.core.config import settings

HOLD_TTL_SECONDS = 300  # 5 minutes


def _get_departure_or_404(db: Session, public_id: str) -> Departure:
    departure = db.query(Departure).filter(Departure.public_id == public_id).first()
    if not departure:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Departure not found")
    return departure


def _calculate_total_amount(departure: Departure, tour, num_adults: int, num_children: int, num_infants: int) -> Decimal:
    adult_price = departure.price_override_adult or tour.base_price_adult
    child_price = departure.price_override_child or tour.base_price_child or Decimal("0")
    # Infants typically travel free or at a nominal fixed rate — using tour's base_price_infant if set
    infant_price = tour.base_price_infant or Decimal("0")

    return (adult_price * num_adults) + (child_price * num_children) + (infant_price * num_infants)


def create_booking(db: Session, current_user: User, payload: BookingCreate) -> Booking:
    departure = _get_departure_or_404(db, payload.departure_public_id)
    tour = departure.tour  # relationship already set up

    if departure.status != DepartureStatusEnum.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This departure is not currently open for booking",
        )

    seats_requested = payload.num_adults + payload.num_children + payload.num_infants

    # --- Redis seat-hold check ---
    currently_held = get_active_holds_count(departure.public_id)
    if (departure.slots_booked + currently_held + seats_requested) > departure.total_slots:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Not enough seats available for this departure",
        )

    hold_id = str(uuid.uuid4())
    acquire_seat_hold(departure.public_id, hold_id, seats_requested, ttl_seconds=HOLD_TTL_SECONDS)

    try:
        total_amount = _calculate_total_amount(
            departure, tour, payload.num_adults, payload.num_children, payload.num_infants
        )

        booking = Booking(
            user_id=current_user.id,
            departure_id=departure.id,
            num_adults=payload.num_adults,
            num_children=payload.num_children,
            num_infants=payload.num_infants,
            total_amount=total_amount,
            status=BookingStatusEnum.pending,
            hold_expires_at=datetime.now(timezone.utc) + timedelta(seconds=HOLD_TTL_SECONDS),
        )
        db.add(booking)
        db.flush()  # get booking.id for travelers

        for traveler in payload.travelers:
            db.add(BookingTraveler(booking_id=booking.id, **traveler.model_dump()))

        db.commit()
        db.refresh(booking)

        # Store the Redis hold_id on the booking's Redis key mapping so we can release it later.
        # (Simplification: hold_id is embedded via booking.public_id lookup at confirm/cancel time.)

    except Exception:
        release_seat_hold(departure.public_id, hold_id)
        db.rollback()
        raise

    return booking


def get_booking_by_public_id(db: Session, public_id: str, current_user: User) -> Booking:
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.travelers), joinedload(Booking.departure))
        .filter(Booking.public_id == public_id)
        .first()
    )
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")

    return booking


def list_my_bookings(db: Session, current_user: User, skip: int = 0, limit: int = 20):
    return (
        db.query(Booking)
        .options(joinedload(Booking.travelers), joinedload(Booking.departure))
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def confirm_booking(db: Session, public_id: str) -> Booking:
    """Called after successful payment (or, for now, manually/for testing).
    Converts the temporary Redis hold into a permanent slots_booked increment."""
    booking = db.query(Booking).filter(Booking.public_id == public_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.status != BookingStatusEnum.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot confirm a booking with status '{booking.status.value}'",
        )

    departure = db.query(Departure).filter(Departure.id == booking.departure_id).first()

    seats = booking.total_travelers
    if departure.slots_booked + seats > departure.total_slots:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seats no longer available — booking cannot be confirmed",
        )

    departure.slots_booked += seats
    if departure.slots_booked >= departure.total_slots:
        departure.status = DepartureStatusEnum.full

    booking.status = BookingStatusEnum.confirmed
    booking.hold_expires_at = None

    db.commit()
    db.refresh(booking)

    # TODO: trigger booking confirmation email (Celery + MS Graph)

    return booking


def cancel_booking(db: Session, public_id: str, current_user: User) -> Booking:
    booking = db.query(Booking).filter(Booking.public_id == public_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")

    if booking.status not in (BookingStatusEnum.pending, BookingStatusEnum.confirmed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a booking with status '{booking.status.value}'",
        )

    was_confirmed = booking.status == BookingStatusEnum.confirmed
    booking.status = BookingStatusEnum.cancelled

    if was_confirmed:
        departure = db.query(Departure).filter(Departure.id == booking.departure_id).first()
        departure.slots_booked -= booking.total_travelers
        if departure.status == DepartureStatusEnum.full:
            departure.status = DepartureStatusEnum.open

    db.commit()
    db.refresh(booking)

    # TODO: trigger refund workflow if payment was already made (Celery task)

    return booking