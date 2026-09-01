from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel


class PublicDestinationOut(BaseModel):
    public_id: str
    name: str
    slug: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class PublicCategoryOut(BaseModel):
    public_id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None

    class Config:
        from_attributes = True


class PublicItineraryDayOut(BaseModel):
    day_number: int
    title: str
    description: str
    meals_included: Optional[str] = None
    accommodation: Optional[str] = None

    class Config:
        from_attributes = True


class PublicTourListItem(BaseModel):
    """Lighter shape for list views — no itinerary, no full description."""
    public_id: str
    title: str
    slug: str
    destination: PublicDestinationOut
    category: PublicCategoryOut
    base_price_adult: Decimal
    duration_days: int
    duration_nights: int
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class PublicTourDetailOut(BaseModel):
    """Full shape for a single tour's detail page."""
    public_id: str
    title: str
    slug: str
    description: str
    destination: PublicDestinationOut
    category: PublicCategoryOut
    base_price_adult: Decimal
    base_price_child: Optional[Decimal] = None
    base_price_infant: Optional[Decimal] = None
    duration_days: int
    duration_nights: int
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    cover_image_url: Optional[str] = None
    gallery_image_urls: Optional[List[str]] = None
    min_group_size: int
    max_group_size: Optional[int] = None
    itinerary_days: List[PublicItineraryDayOut] = []

    class Config:
        from_attributes = True


class PublicDepartureOut(BaseModel):
    public_id: str
    start_date: date
    end_date: date
    available_slots: int
    price_override_adult: Optional[Decimal] = None
    price_override_child: Optional[Decimal] = None

    class Config:
        from_attributes = True