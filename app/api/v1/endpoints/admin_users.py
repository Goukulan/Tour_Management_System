from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.models.users import User
from app.models.users import RoleEnum
from app.schemas.admin_user import AdminUserOut, UpdateUserStatusRequest
from app.services import admin_user_service

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["Admin - Users"],
)


@router.get("", response_model=List[AdminUserOut])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[RoleEnum] = Query(None),
    only_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_user_service.list_users(
        db, skip=skip, limit=limit, role=role, only_active=only_active, search=search
    )


@router.get("/{public_id}", response_model=AdminUserOut)
def get_user(
    public_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return admin_user_service.get_user_by_public_id(db, public_id)


@router.patch("/{public_id}/status", response_model=AdminUserOut)
def update_user_status(
    public_id: str,
    payload: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return admin_user_service.update_user_status(db, public_id, payload, current_admin)