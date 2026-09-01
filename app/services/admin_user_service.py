from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.users import User
from app.models.users import RoleEnum
from app.schemas.admin_user import UpdateUserStatusRequest


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    role: Optional[RoleEnum] = None,
    only_active: Optional[bool] = None,
    search: Optional[str] = None,
):
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if only_active is not None:
        query = query.filter(User.is_active == only_active)

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.full_name.ilike(like_pattern),
                User.email.ilike(like_pattern),
            )
        )

    return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()


def get_user_by_public_id(db: Session, public_id: str) -> User:
    user = db.query(User).filter(User.public_id == public_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def update_user_status(db: Session, public_id: str, payload: UpdateUserStatusRequest, current_admin: User) -> User:
    user = get_user_by_public_id(db, public_id)

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own admin account",
        )

    if user.role == RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin accounts cannot be deactivated through this endpoint",
        )

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return user