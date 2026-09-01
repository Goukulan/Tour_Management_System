from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services import booking_service

router = APIRouter(prefix="/api/v1/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.create_booking(db, current_user, payload)


@router.get("/my", response_model=List[BookingOut])
def list_my_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.list_my_bookings(db, current_user, skip=skip, limit=limit)


@router.get("/{public_id}", response_model=BookingOut)
def get_booking(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.get_booking_by_public_id(db, public_id, current_user)


@router.post("/{public_id}/cancel", response_model=BookingOut)
def cancel_booking(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return booking_service.cancel_booking(db, public_id, current_user)