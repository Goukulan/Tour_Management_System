from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.models.booking import BookingStatusEnum


class TravelerInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None


class BookingCreate(BaseModel):
    departure_public_id: str
    num_adults: int = Field(ge=1)
    num_children: int = Field(default=0, ge=0)
    num_infants: int = Field(default=0, ge=0)
    travelers: List[TravelerInput]

    @field_validator("travelers")
    @classmethod
    def traveler_count_matches(cls, v: List[TravelerInput], info) -> List[TravelerInput]:
        data = info.data
        if "num_adults" in data and "num_children" in data:
            expected = data["num_adults"] + data["num_children"] + data.get("num_infants", 0)
            if len(v) != expected:
                raise ValueError(
                    f"Number of travelers ({len(v)}) must match num_adults + num_children + num_infants ({expected})"
                )
        return v


class TravelerOut(BaseModel):
    public_id: str
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None

    class Config:
        from_attributes = True


class BookingOut(BaseModel):
    public_id: str
    departure_public_id: str
    num_adults: int
    num_children: int
    num_infants: int
    total_travelers: int
    total_amount: Decimal
    status: BookingStatusEnum
    hold_expires_at: Optional[datetime] = None
    travelers: List[TravelerOut] = []
    created_at: datetime

    class Config:
        from_attributes = True