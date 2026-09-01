import enum
from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.utils.security import generate_short_id


class BookingStatusEnum(str, enum.Enum):
    pending = "pending"        # seat held, awaiting payment
    confirmed = "confirmed"    # payment done, seat locked in
    ongoing = "ongoing"        # departure has started
    completed = "completed"    # departure finished
    cancelled = "cancelled"
    refunded = "refunded"


class Booking(Base):
    __tablename__ = "bookings"

    id                  = Column(Integer, primary_key=True, index=True)
    public_id           = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    user_id             = Column(Integer, ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, index=True)
    departure_id        = Column(Integer, ForeignKey("departures.id", ondelete="RESTRICT"), nullable=False, index=True)

    num_adults          = Column(Integer, nullable=False, default=1)
    num_children        = Column(Integer, nullable=False, default=0)
    num_infants         = Column(Integer, nullable=False, default=0)

    total_amount        = Column(Numeric(10, 2), nullable=False)

    status              = Column(Enum(BookingStatusEnum, name="booking_status_enum"), default=BookingStatusEnum.pending, nullable=False, index=True)

    hold_expires_at     = Column(DateTime(timezone=True), nullable=True)  # only relevant while status=pending

    created_at          = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user                = relationship("User", backref="bookings")
    departure           = relationship("Departure", backref="bookings")
    travelers           = relationship("BookingTraveler", back_populates="booking", cascade="all, delete-orphan")

    @property
    def total_travelers(self) -> int:
        return self.num_adults + self.num_children + self.num_infants

    def __repr__(self) -> str:
        return f"<Booking id={self.id} status={self.status} departure_id={self.departure_id}>"

    @property
    def departure_public_id(self):
        return self.departure.public_id if self.departure else None