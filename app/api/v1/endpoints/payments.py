from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_user
from app.models.users import User
from app.schemas.payment import PaymentOrderOut, PaymentVerifyRequest
from app.schemas.booking import BookingOut
from app.services import payment_service
from app.core.config import settings

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("/{booking_public_id}/order", response_model=PaymentOrderOut)
def create_order(booking_public_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    payment = payment_service.create_payment_order(db, booking_public_id, current_user)
    return PaymentOrderOut(
        booking_public_id=booking_public_id,
        razorpay_order_id=payment.razorpay_order_id,
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        amount=payment.amount,
    )


@router.post("/verify", response_model=BookingOut)
def verify_payment(payload: PaymentVerifyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return payment_service.verify_and_confirm_payment(db, payload)