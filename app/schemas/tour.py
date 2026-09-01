from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.tour_itinerary_day import ItineraryDayCreate, ItineraryDayOut
from app.schemas.destination import DestinationOut
from app.schemas.category import CategoryOut


class TourCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=220)
    description: str

    destination_public_id: str
    category_public_id: str

    base_price_adult: Decimal = Field(gt=0)
    base_price_child: Optional[Decimal] = Field(default=None, ge=0)
    base_price_infant: Optional[Decimal] = Field(default=None, ge=0)

    duration_days: int = Field(ge=1)
    duration_nights: int = Field(ge=0)

    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None

    cover_image_url: Optional[str] = None
    gallery_image_urls: Optional[List[str]] = None

    min_group_size: int = Field(default=1, ge=1)
    max_group_size: Optional[int] = Field(default=None, ge=1)

    itinerary_days: Optional[List[ItineraryDayCreate]] = None


class TourUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    slug: Optional[str] = Field(default=None, min_length=2, max_length=220)
    description: Optional[str] = None

    destination_public_id: Optional[str] = None
    category_public_id: Optional[str] = None

    base_price_adult: Optional[Decimal] = Field(default=None, gt=0)
    base_price_child: Optional[Decimal] = Field(default=None, ge=0)
    base_price_infant: Optional[Decimal] = Field(default=None, ge=0)

    duration_days: Optional[int] = Field(default=None, ge=1)
    duration_nights: Optional[int] = Field(default=None, ge=0)

    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None

    cover_image_url: Optional[str] = None
    gallery_image_urls: Optional[List[str]] = None

    min_group_size: Optional[int] = Field(default=None, ge=1)
    max_group_size: Optional[int] = Field(default=None, ge=1)

    is_active: Optional[bool] = None


class TourOut(BaseModel):
    public_id: str
    title: str
    slug: str
    description: str

    destination: DestinationOut
    category: CategoryOut

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

    is_active: bool
    created_at: datetime

    itinerary_days: List[ItineraryDayOut] = []

    class Config:
        from_attributes = True