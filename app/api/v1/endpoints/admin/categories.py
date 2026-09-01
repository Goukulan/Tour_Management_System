from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services import category_service

router = APIRouter(
    prefix="/api/v1/admin/categories",
    tags=["Admin - Categories"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, payload)


@router.get("", response_model=List[CategoryOut])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_active: bool = Query(False),
    db: Session = Depends(get_db),
):
    return category_service.list_categories(db, skip=skip, limit=limit, only_active=only_active)


@router.get("/{public_id}", response_model=CategoryOut)
def get_category(public_id: str, db: Session = Depends(get_db)):
    return category_service.get_category_by_public_id(db, public_id)


@router.patch("/{public_id}", response_model=CategoryOut)
def update_category(public_id: str, payload: CategoryUpdate, db: Session = Depends(get_db)):
    return category_service.update_category(db, public_id, payload)


@router.delete("/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(public_id: str, db: Session = Depends(get_db)):
    category_service.delete_category(db, public_id)
    return None