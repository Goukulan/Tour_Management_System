from decimal import Decimal
from pydantic import BaseModel


class PaymentOrderOut(BaseModel):
    booking_public_id: str
    razorpay_order_id: str
    razorpay_key_id: str
    amount: Decimal
    currency: str = "INR"


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str