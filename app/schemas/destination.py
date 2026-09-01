from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DestinationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=140)
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    slug: Optional[str] = Field(default=None, min_length=2, max_length=140)
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_active: Optional[bool] = None


class DestinationOut(BaseModel):
    public_id: str
    name: str
    slug: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True