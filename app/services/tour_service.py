from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.tour import Tour
from app.models.destination import Destination
from app.models.category import Category
from app.models.tour_itinerary_day import TourItineraryDay
from app.schemas.tour import TourCreate, TourUpdate
from app.schemas.tour_itinerary_day import ItineraryDayCreate, ItineraryDayUpdate

from sqlalchemy import and_
from decimal import Decimal
from datetime import date as date_type



def _resolve_destination(db: Session, public_id: str) -> Destination:
    destination = db.query(Destination).filter(Destination.public_id == public_id).first()
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found",
        )
    return destination


def _resolve_category(db: Session, public_id: str) -> Category:
    category = db.query(Category).filter(Category.public_id == public_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


def create_tour(db: Session, payload: TourCreate) -> Tour:
    existing = db.query(Tour).filter(Tour.slug == payload.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A tour with this slug already exists",
        )

    destination = _resolve_destination(db, payload.destination_public_id)
    category = _resolve_category(db, payload.category_public_id)

    data = payload.model_dump(exclude={"destination_public_id", "category_public_id", "itinerary_days"})

    tour = Tour(
        **data,
        destination_id=destination.id,
        category_id=category.id,
    )
    db.add(tour)
    db.flush()  # get tour.id without committing yet, so itinerary days can reference it

    if payload.itinerary_days:
        _create_itinerary_days(db, tour.id, payload.itinerary_days)

    db.commit()
    db.refresh(tour)
    return tour


def _create_itinerary_days(db: Session, tour_id: int, days: list[ItineraryDayCreate]) -> None:
    day_numbers = [d.day_number for d in days]
    if len(day_numbers) != len(set(day_numbers)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate day_number values found in itinerary_days",
        )

    for day in days:
        db.add(TourItineraryDay(tour_id=tour_id, **day.model_dump()))


def get_tour_by_public_id(db: Session, public_id: str) -> Tour:
    tour = (
        db.query(Tour)
        .options(joinedload(Tour.destination), joinedload(Tour.category), joinedload(Tour.itinerary_days))
        .filter(Tour.public_id == public_id)
        .first()
    )
    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found",
        )
    return tour


def list_tours(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    only_active: bool = False,
    destination_public_id: str | None = None,
    category_public_id: str | None = None,
):
    query = db.query(Tour).options(joinedload(Tour.destination), joinedload(Tour.category))

    if only_active:
        query = query.filter(Tour.is_active == True)

    if destination_public_id:
        query = query.join(Destination).filter(Destination.public_id == destination_public_id)

    if category_public_id:
        query = query.join(Category).filter(Category.public_id == category_public_id)

    return query.offset(skip).limit(limit).all()


def update_tour(db: Session, public_id: str, payload: TourUpdate) -> Tour:
    tour = get_tour_by_public_id(db, public_id)

    update_data = payload.model_dump(exclude_unset=True, exclude={"destination_public_id", "category_public_id"})

    if "slug" in update_data and update_data["slug"] != tour.slug:
        existing = db.query(Tour).filter(Tour.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A tour with this slug already exists",
            )

    if payload.destination_public_id:
        tour.destination_id = _resolve_destination(db, payload.destination_public_id).id

    if payload.category_public_id:
        tour.category_id = _resolve_category(db, payload.category_public_id).id

    for field, value in update_data.items():
        setattr(tour, field, value)

    db.commit()
    db.refresh(tour)
    return tour


def delete_tour(db: Session, public_id: str) -> None:
    tour = get_tour_by_public_id(db, public_id)

    if tour.departures:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a tour with existing departures. Deactivate it instead.",
        )

    db.delete(tour)
    db.commit()


# ---------- Itinerary Day management (add/edit/remove after tour creation) ----------

def add_itinerary_day(db: Session, tour_public_id: str, payload: ItineraryDayCreate) -> TourItineraryDay:
    tour = get_tour_by_public_id(db, tour_public_id)

    existing = (
        db.query(TourItineraryDay)
        .filter(TourItineraryDay.tour_id == tour.id, TourItineraryDay.day_number == payload.day_number)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Day {payload.day_number} already exists for this tour",
        )

    day = TourItineraryDay(tour_id=tour.id, **payload.model_dump())
    db.add(day)
    db.commit()
    db.refresh(day)
    return day


def delete_itinerary_day(db: Session, tour_public_id: str, day_number: int) -> None:
    tour = get_tour_by_public_id(db, tour_public_id)

    day = (
        db.query(TourItineraryDay)
        .filter(TourItineraryDay.tour_id == tour.id, TourItineraryDay.day_number == day_number)
        .first()
    )
    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary day not found",
        )

    db.delete(day)
    db.commit()

def update_itinerary_day(
    db: Session, tour_public_id: str, day_number: int, payload: ItineraryDayUpdate
) -> TourItineraryDay:
    tour = get_tour_by_public_id(db, tour_public_id)

    day = (
        db.query(TourItineraryDay)
        .filter(TourItineraryDay.tour_id == tour.id, TourItineraryDay.day_number == day_number)
        .first()
    )
    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary day not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    new_day_number = update_data.get("day_number")
    if new_day_number is not None and new_day_number != day.day_number:
        clash = (
            db.query(TourItineraryDay)
            .filter(TourItineraryDay.tour_id == tour.id, TourItineraryDay.day_number == new_day_number)
            .first()
        )
        if clash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Day {new_day_number} already exists for this tour",
            )

    for field, value in update_data.items():
        setattr(day, field, value)

    db.commit()
    db.refresh(day)
    return day


def search_public_tours(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    destination_public_id: str | None = None,
    category_public_id: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_duration_days: int | None = None,
    max_duration_days: int | None = None,
    keyword: str | None = None,
):
    query = (
        db.query(Tour)
        .options(joinedload(Tour.destination), joinedload(Tour.category))
        .filter(Tour.is_active == True)
    )

    if destination_public_id:
        query = query.join(Destination).filter(Destination.public_id == destination_public_id)

    if category_public_id:
        query = query.join(Category).filter(Category.public_id == category_public_id)

    if min_price is not None:
        query = query.filter(Tour.base_price_adult >= min_price)

    if max_price is not None:
        query = query.filter(Tour.base_price_adult <= max_price)

    if min_duration_days is not None:
        query = query.filter(Tour.duration_days >= min_duration_days)

    if max_duration_days is not None:
        query = query.filter(Tour.duration_days <= max_duration_days)

    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(Tour.title.ilike(like_pattern))

    return query.offset(skip).limit(limit).all()


def get_public_tour_by_slug(db: Session, slug: str) -> Tour:
    tour = (
        db.query(Tour)
        .options(joinedload(Tour.destination), joinedload(Tour.category), joinedload(Tour.itinerary_days))
        .filter(Tour.slug == slug, Tour.is_active == True)
        .first()
    )
    if not tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found")
    return tour