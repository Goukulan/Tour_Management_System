from sqlalchemy import (
    Column, Integer, String, Date, Numeric, DateTime, Enum, ForeignKey, func
)
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.utils.security import generate_short_id
import enum


class DepartureStatusEnum(str, enum.Enum):
    open = "open"
    full = "full"
    cancelled = "cancelled"
    completed = "completed"


class Departure(Base):
    __tablename__ = "departures"

    id                     = Column(Integer, primary_key=True, index=True)
    public_id              = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    tour_id                = Column(Integer, ForeignKey("tours.id", ondelete="CASCADE"), nullable=False, index=True)

    start_date             = Column(Date, nullable=False)
    end_date               = Column(Date, nullable=False)

    total_slots            = Column(Integer, nullable=False)
    slots_booked           = Column(Integer, default=0, nullable=False)

    price_override_adult   = Column(Numeric(10, 2), nullable=True)
    price_override_child   = Column(Numeric(10, 2), nullable=True)

    status                 = Column(Enum(DepartureStatusEnum, name="departure_status_enum"), default=DepartureStatusEnum.open, nullable=False, index=True)

    created_at             = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at             = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    actual_start_at        = Column(DateTime(timezone=True), nullable=True)
    actual_end_at          = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    tour                    = relationship("Tour", back_populates="departures")

    @property
    def available_slots(self) -> int:
        return self.total_slots - self.slots_booked

    @property
    def tour_public_id(self) -> str:
        return self.tour.public_id

    def __repr__(self) -> str:
        return f"<Departure id={self.id} tour_id={self.tour_id} start={self.start_date}>"