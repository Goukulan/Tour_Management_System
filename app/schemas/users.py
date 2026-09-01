from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.users import RoleEnum, GenderEnum


# ---------- Request Schemas ----------

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    confirm_password: str = Field(min_length=8, max_length=72)
    phone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=72)
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=72)
    confirm_new_password: str

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


# ---------- Response Schemas ----------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    # refresh_token intentionally NOT here — it goes in an HttpOnly cookie, not the JSON body


class UserOut(BaseModel):
    public_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: RoleEnum
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_first_login: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserOut
    tokens: TokenResponse