from typing import List

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.utils.dependencies import get_current_admin
from app.schemas.guide import GuideCreate, GuideUpdate, GuideOut, GuideAssignmentOut
from app.services import guide_service

router = APIRouter(
    prefix="/api/v1/admin/guides",
    tags=["Admin - Guides"],
    dependencies=[Depends(get_current_admin)],
)


@router.post("", response_model=GuideOut, status_code=status.HTTP_201_CREATED)
def create_guide(payload: GuideCreate, db: Session = Depends(get_db)):
    return guide_service.create_guide(db, payload)


@router.get("", response_model=List[GuideOut])
def list_guides(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    only_active: bool = Query(False),
    db: Session = Depends(get_db),
):
    return guide_service.list_guides(db, skip=skip, limit=limit, only_active=only_active)


@router.get("/{public_id}", response_model=GuideOut)
def get_guide(public_id: str, db: Session = Depends(get_db)):
    return guide_service.get_guide_by_public_id(db, public_id)


@router.patch("/{public_id}", response_model=GuideOut)
def update_guide(public_id: str, payload: GuideUpdate, db: Session = Depends(get_db)):
    return guide_service.update_guide(db, public_id, payload)


@router.post("/{public_id}/deactivate", response_model=GuideOut)
def deactivate_guide(public_id: str, db: Session = Depends(get_db)):
    return guide_service.deactivate_guide(db, public_id)


# ---------- Assignment routes ----------

@router.post("/{public_id}/assign/{departure_public_id}", response_model=GuideAssignmentOut, status_code=status.HTTP_201_CREATED)
def assign_guide(public_id: str, departure_public_id: str, db: Session = Depends(get_db)):
    assignment = guide_service.assign_guide_to_departure(db, public_id, departure_public_id)
    return GuideAssignmentOut(
        guide=assignment.guide,
        departure_public_id=assignment.departure.public_id,
        assigned_at=assignment.assigned_at,
    )


@router.delete("/{public_id}/assign/{departure_public_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_guide(public_id: str, departure_public_id: str, db: Session = Depends(get_db)):
    guide_service.unassign_guide_from_departure(db, public_id, departure_public_id)
    return None