from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.destination import Destination
from app.schemas.destination import DestinationCreate, DestinationUpdate


def create_destination(db: Session, payload: DestinationCreate) -> Destination:
    existing = db.query(Destination).filter(Destination.slug == payload.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A destination with this slug already exists",
        )

    destination = Destination(**payload.model_dump())
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return destination


def get_destination_by_public_id(db: Session, public_id: str) -> Destination:
    destination = db.query(Destination).filter(Destination.public_id == public_id).first()
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found",
        )
    return destination


def list_destinations(db: Session, skip: int = 0, limit: int = 20, only_active: bool = False):
    query = db.query(Destination)
    if only_active:
        query = query.filter(Destination.is_active == True)
    return query.offset(skip).limit(limit).all()


def update_destination(db: Session, public_id: str, payload: DestinationUpdate) -> Destination:
    destination = get_destination_by_public_id(db, public_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != destination.slug:
        existing = db.query(Destination).filter(Destination.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A destination with this slug already exists",
            )

    for field, value in update_data.items():
        setattr(destination, field, value)

    db.commit()
    db.refresh(destination)
    return destination


def delete_destination(db: Session, public_id: str) -> None:
    destination = get_destination_by_public_id(db, public_id)

    if destination.tours:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a destination with existing tours. Deactivate it instead.",
        )

    db.delete(destination)
    db.commit()