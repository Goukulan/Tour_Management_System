from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.schemas.booking import BookingOut
from app.services import booking_service

router = APIRouter(
    prefix="/api/v1/admin/bookings",
    tags=["Admin - Bookings"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("/{public_id}/force-confirm", response_model=BookingOut)
def force_confirm_booking(public_id: str, db: Session = Depends(get_db)):
    """
    TEMPORARY endpoint — simulates a successful payment confirming a booking.
    Remove or gate this once real Payments (Stripe/Razorpay webhook) is built,
    since that will be what actually calls booking_service.confirm_booking().
    """
    return booking_service.confirm_booking(db, public_id)