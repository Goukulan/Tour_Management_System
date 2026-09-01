from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.constants.enums import PaymentStatusEnum
from app.utils.security import generate_short_id


class Payment(Base):
    __tablename__ = "payments"

    id                  = Column(Integer, primary_key=True, index=True)
    public_id           = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    booking_id          = Column(Integer, ForeignKey("bookings.id", ondelete="RESTRICT"), nullable=False, index=True)

    razorpay_order_id   = Column(String, unique=True, nullable=False, index=True)
    razorpay_payment_id = Column(String, unique=True, nullable=True)
    razorpay_signature  = Column(String, nullable=True)

    amount              = Column(Numeric(10, 2), nullable=False)
    status              = Column(Enum(PaymentStatusEnum, name="payment_status_enum"), default=PaymentStatusEnum.created, nullable=False, index=True)

    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    booking             = relationship("Booking", backref="payments")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} booking_id={self.booking_id} status={self.status}>"