from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.departure import DepartureStatusEnum


class DepartureCreate(BaseModel):
    start_date: date
    end_date: date
    total_slots: int = Field(gt=0)
    price_override_adult: Optional[Decimal] = Field(default=None, gt=0)
    price_override_child: Optional[Decimal] = Field(default=None, ge=0)

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on or after start_date")
        return v


class DepartureUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_slots: Optional[int] = Field(default=None, gt=0)
    price_override_adult: Optional[Decimal] = Field(default=None, gt=0)
    price_override_child: Optional[Decimal] = Field(default=None, ge=0)
    status: Optional[DepartureStatusEnum] = None


class DepartureOut(BaseModel):
    public_id: str
    tour_public_id: str
    start_date: date
    end_date: date
    total_slots: int
    slots_booked: int
    available_slots: int
    price_override_adult: Optional[Decimal] = None
    price_override_child: Optional[Decimal] = None
    status: DepartureStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True