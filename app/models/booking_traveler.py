from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.utils.security import generate_short_id


class BookingTraveler(Base):
    __tablename__ = "booking_travelers"

    id            = Column(Integer, primary_key=True, index=True)
    booking_id    = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)

    full_name     = Column(String, nullable=False)
    age           = Column(Integer, nullable=True)
    gender        = Column(String, nullable=True)
    id_proof_type = Column(String, nullable=True)   # e.g. "Aadhaar", "Passport"
    id_proof_number = Column(String, nullable=True)

    public_id = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    # Relationship
    booking       = relationship("Booking", back_populates="travelers")

    def __repr__(self) -> str:
        return f"<BookingTraveler id={self.id} booking_id={self.booking_id} name={self.full_name}>"