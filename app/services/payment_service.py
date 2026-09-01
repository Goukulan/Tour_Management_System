from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import razorpay.errors

from pathlib import Path
from app.models.booking import Booking
from app.models.payment import Payment
from app.constants.enums import BookingStatusEnum, PaymentStatusEnum
from app.core.razorpay_client import razorpay_client
from app.core.config import settings
from app.services import booking_service
from app.services.email_service import send_email



def create_payment_order(db: Session, booking_public_id: str, current_user) -> Payment:
    booking = db.query(Booking).filter(Booking.public_id == booking_public_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your booking")

    if booking.status != BookingStatusEnum.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot initiate payment for a booking with status '{booking.status.value}'",
        )

    # Razorpay expects amount in the smallest currency unit (paise for INR)
    amount_paise = int(booking.total_amount * 100)

    order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": booking.public_id,
        "notes": {"booking_public_id": booking.public_id},
    })

    payment = Payment(
        booking_id=booking.id,
        razorpay_order_id=order["id"],
        amount=booking.total_amount,
        status=PaymentStatusEnum.created,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def verify_and_confirm_payment(db: Session, payload) -> Booking:
    payment = db.query(Payment).filter(Payment.razorpay_order_id == payload.razorpay_order_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment order not found")

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": payload.razorpay_order_id,
            "razorpay_payment_id": payload.razorpay_payment_id,
            "razorpay_signature": payload.razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        payment.status = PaymentStatusEnum.failed
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment signature verification failed")

    payment.razorpay_payment_id = payload.razorpay_payment_id
    payment.razorpay_signature = payload.razorpay_signature
    payment.status = PaymentStatusEnum.paid
    db.commit()

    booking = booking_service.confirm_booking(db, payment.booking.public_id)

    template = Path("app/templates/booking_confirmation.html").read_text()
    html = (
        template
        .replace("{{ full_name }}", booking.user.full_name)
        .replace("{{ booking_public_id }}", booking.public_id)
        .replace("{{ tour_title }}", booking.departure.tour.title)
        .replace("{{ start_date }}", str(booking.departure.start_date))
        .replace("{{ end_date }}", str(booking.departure.end_date))
        .replace("{{ total_travelers }}", str(booking.total_travelers))
        .replace("{{ total_amount }}", str(booking.total_amount))
    )

    try:
        send_email(booking.user.email, "Your Tour Booking is Confirmed!", html)
    except Exception as e:
        print(f"Email sending failed: {e}")  # don't let email failure break the payment flow

    return booking