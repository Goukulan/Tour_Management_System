from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel


class GuideDepartureOut(BaseModel):
    public_id: str
    tour_title: str
    start_date: date
    end_date: date
    total_slots: int
    slots_booked: int
    status: str
    actual_start_at: Optional[datetime] = None
    actual_end_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TravelerRosterItem(BaseModel):
    public_id: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    booking_public_id: str
    booker_name: str
    booker_phone: Optional[str] = None
    is_checked_in: bool = False

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    traveler_public_id: str
    present: bool = True


class AttendanceOut(BaseModel):
    traveler_public_id: str
    traveler_name: str
    present: bool
    checked_in_at: datetime