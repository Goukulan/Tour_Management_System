from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    slug: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    slug: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryOut(BaseModel):
    public_id: str
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True