from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, func
)
from sqlalchemy.orm import relationship

from app.core.db import Base


class TourItineraryDay(Base):
    __tablename__ = "tour_itinerary_days"

    __table_args__ = (
        UniqueConstraint("tour_id", "day_number", name="uix_tour_day_number"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    tour_id          = Column(Integer, ForeignKey("tours.id", ondelete="CASCADE"), nullable=False, index=True)

    day_number       = Column(Integer, nullable=False)
    title            = Column(String, nullable=False)
    description      = Column(Text, nullable=False)
    meals_included   = Column(String, nullable=True)
    accommodation    = Column(String, nullable=True)

    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at       = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship
    tour             = relationship("Tour", back_populates="itinerary_days")

    def __repr__(self) -> str:
        return f"<TourItineraryDay tour_id={self.tour_id} day={self.day_number}>"