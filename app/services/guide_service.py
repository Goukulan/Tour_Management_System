from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.users import User
from app.models.departure import Departure
from app.models.guide_assignment import GuideAssignment
from app.models.users import RoleEnum
from app.schemas.guide import GuideCreate, GuideUpdate
from app.utils.security import hash_password


def create_guide(db: Session, payload: GuideCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    guide = User(
        full_name=payload.full_name,
        email=payload.email,
        password=hash_password(payload.password),
        phone=payload.phone,
        role=RoleEnum.guide,
        is_verified=True,     # admin-created, skip email verification
        is_first_login=True,  # force password change on first login
    )
    db.add(guide)
    db.commit()
    db.refresh(guide)
    return guide


def _get_guide_or_404(db: Session, public_id: str) -> User:
    guide = db.query(User).filter(User.public_id == public_id, User.role == RoleEnum.guide).first()
    if not guide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guide not found",
        )
    return guide


def get_guide_by_public_id(db: Session, public_id: str) -> User:
    return _get_guide_or_404(db, public_id)


def list_guides(db: Session, skip: int = 0, limit: int = 20, only_active: bool = False):
    query = db.query(User).filter(User.role == RoleEnum.guide)
    if only_active:
        query = query.filter(User.is_active == True)
    return query.offset(skip).limit(limit).all()


def update_guide(db: Session, public_id: str, payload: GuideUpdate) -> User:
    guide = _get_guide_or_404(db, public_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(guide, field, value)

    db.commit()
    db.refresh(guide)
    return guide


def deactivate_guide(db: Session, public_id: str) -> User:
    guide = _get_guide_or_404(db, public_id)
    guide.is_active = False
    db.commit()
    db.refresh(guide)
    return guide


# ---------- Assignment logic ----------

def _get_departure_or_404(db: Session, departure_public_id: str) -> Departure:
    departure = db.query(Departure).filter(Departure.public_id == departure_public_id).first()
    if not departure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Departure not found",
        )
    return departure


def assign_guide_to_departure(db: Session, guide_public_id: str, departure_public_id: str) -> GuideAssignment:
    guide = _get_guide_or_404(db, guide_public_id)
    departure = _get_departure_or_404(db, departure_public_id)

    existing = (
        db.query(GuideAssignment)
        .filter(GuideAssignment.guide_id == guide.id, GuideAssignment.departure_id == departure.id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This guide is already assigned to this departure",
        )

    assignment = GuideAssignment(guide_id=guide.id, departure_id=departure.id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def unassign_guide_from_departure(db: Session, guide_public_id: str, departure_public_id: str) -> None:
    guide = _get_guide_or_404(db, guide_public_id)
    departure = _get_departure_or_404(db, departure_public_id)

    assignment = (
        db.query(GuideAssignment)
        .filter(GuideAssignment.guide_id == guide.id, GuideAssignment.departure_id == departure.id)
        .first()
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This guide is not assigned to this departure",
        )

    db.delete(assignment)
    db.commit()


def list_assignments_for_departure(db: Session, departure_public_id: str):
    departure = _get_departure_or_404(db, departure_public_id)
    return db.query(GuideAssignment).filter(GuideAssignment.departure_id == departure.id).all()