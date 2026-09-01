from typing import Optional

from pydantic import BaseModel, Field


class ItineraryDayCreate(BaseModel):
    day_number: int = Field(ge=1)
    title: str = Field(min_length=2, max_length=150)
    description: str
    meals_included: Optional[str] = None
    accommodation: Optional[str] = None


class ItineraryDayUpdate(BaseModel):
    day_number: Optional[int] = Field(default=None, ge=1)
    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = None
    meals_included: Optional[str] = None
    accommodation: Optional[str] = None


class ItineraryDayOut(BaseModel):
    day_number: int
    title: str
    description: str
    meals_included: Optional[str] = None
    accommodation: Optional[str] = None

    class Config:
        from_attributes = True