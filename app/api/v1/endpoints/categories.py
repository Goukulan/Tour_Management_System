from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.public import PublicCategoryOut
from app.services import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["Public - Categories"])


@router.get("", response_model=List[PublicCategoryOut])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return category_service.list_categories(db, skip=skip, limit=limit, only_active=True)