from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.models.users import User
from app.schemas.destination import DestinationCreate, DestinationUpdate, DestinationOut
from app.services import destination_service

router = APIRouter(
    prefix="/api/v1/admin/destinations",
    tags=["Admin - Destinations"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=DestinationOut, status_code=status.HTTP_201_CREATED)
def create_destination(payload: DestinationCreate, db: Session = Depends(get_db)):
    return destination_service.create_destination(db, payload)


@router.get("", response_model=List[DestinationOut])
def list_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_active: bool = Query(False),
    db: Session = Depends(get_db),
):
    return destination_service.list_destinations(db, skip=skip, limit=limit, only_active=only_active)


@router.get("/{public_id}", response_model=DestinationOut)
def get_destination(public_id: str, db: Session = Depends(get_db)):
    return destination_service.get_destination_by_public_id(db, public_id)


@router.patch("/{public_id}", response_model=DestinationOut)
def update_destination(public_id: str, payload: DestinationUpdate, db: Session = Depends(get_db)):
    return destination_service.update_destination(db, public_id, payload)


@router.delete("/{public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(public_id: str, db: Session = Depends(get_db)):
    destination_service.delete_destination(db, public_id)
    return None