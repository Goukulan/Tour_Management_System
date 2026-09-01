# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users import User, RoleEnum
from app.schemas.users import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password=hash_password(payload.password),
        phone=payload.phone,
        role=RoleEnum.user,  # hardcoded — never trust client input for role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: trigger email verification task here (Celery + MS Graph email)

    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    return user


def issue_tokens(user: User) -> tuple[str, str]:
    """Returns (access_token, refresh_token). Caller decides where each goes
    (access -> JSON body, refresh -> HttpOnly cookie)."""
    token_data = {"sub": user.public_id, "role": user.role.value}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return access_token, refresh_token


def rotate_refresh_token(db: Session, refresh_token: str) -> tuple[str, str]:
    """Validates an incoming refresh token and issues a new access+refresh pair."""
    payload = decode_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    public_id = payload.get("sub")
    user = db.query(User).filter(User.public_id == public_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return issue_tokens(user)