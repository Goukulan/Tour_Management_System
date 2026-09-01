from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.db import Base


class Attendance(Base):
    __tablename__ = "attendances"

    __table_args__ = (
        UniqueConstraint("departure_id", "booking_traveler_id", name="uix_attendance_traveler"),
    )

    id                  = Column(Integer, primary_key=True, index=True)
    departure_id        = Column(Integer, ForeignKey("departures.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_traveler_id = Column(Integer, ForeignKey("booking_travelers.id", ondelete="CASCADE"), nullable=False, index=True)
    marked_by_guide_id  = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)

    present             = Column(Boolean, nullable=False, default=True)
    checked_in_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    departure           = relationship("Departure", backref="attendances")
    traveler             = relationship("BookingTraveler", backref="attendance")
    marked_by_guide       = relationship("User")

    def __repr__(self) -> str:
        return f"<Attendance departure_id={self.departure_id} traveler_id={self.booking_traveler_id} present={self.present}>"