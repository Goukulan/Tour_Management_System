from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.users import RoleEnum, GenderEnum


class AdminUserOut(BaseModel):
    public_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: RoleEnum
    phone: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateUserStatusRequest(BaseModel):
    is_active: bool