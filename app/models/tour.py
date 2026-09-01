from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric, DateTime, ForeignKey, JSON, func
)
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.utils.security import generate_short_id


class Tour(Base):
    __tablename__ = "tours"

    id                   = Column(Integer, primary_key=True, index=True)
    public_id            = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    title                = Column(String, nullable=False)
    slug                 = Column(String, unique=True, index=True, nullable=False)
    description          = Column(Text, nullable=False)

    destination_id       = Column(Integer, ForeignKey("destinations.id", ondelete="RESTRICT"), nullable=False, index=True)
    category_id          = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)

    base_price_adult     = Column(Numeric(10, 2), nullable=False)
    base_price_child     = Column(Numeric(10, 2), nullable=True)
    base_price_infant    = Column(Numeric(10, 2), nullable=True)

    duration_days        = Column(Integer, nullable=False)
    duration_nights      = Column(Integer, nullable=False)

    inclusions           = Column(JSON, nullable=True)   # e.g. ["Hotel stay", "Breakfast", "Airport transfer"]
    exclusions           = Column(JSON, nullable=True)   # e.g. ["Lunch", "Personal expenses"]

    cover_image_url      = Column(String, nullable=True)
    gallery_image_urls   = Column(JSON, nullable=True)   # e.g. ["url1", "url2", "url3"]

    min_group_size       = Column(Integer, default=1, nullable=False)
    max_group_size       = Column(Integer, nullable=True)

    is_active            = Column(Boolean, default=True, nullable=False)

    created_at           = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at           = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    destination          = relationship("Destination", backref="tours")
    category              = relationship("Category", backref="tours")
    itinerary_days        = relationship("TourItineraryDay", back_populates="tour", cascade="all, delete-orphan", order_by="TourItineraryDay.day_number")
    departures             = relationship("Departure", back_populates="tour", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tour id={self.id} title={self.title}>"