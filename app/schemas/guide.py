from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class GuideCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = Field(default=None, max_length=20)


class GuideUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class GuideOut(BaseModel):
    public_id: str
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GuideAssignmentOut(BaseModel):
    guide: GuideOut
    departure_public_id: str
    assigned_at: datetime

    class Config:
        from_attributes = True