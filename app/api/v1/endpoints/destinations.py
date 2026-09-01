from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.public import PublicDestinationOut
from app.services import destination_service

router = APIRouter(prefix="/api/v1/destinations", tags=["Public - Destinations"])


@router.get("", response_model=List[PublicDestinationOut])
def list_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return destination_service.list_destinations(db, skip=skip, limit=limit, only_active=True)