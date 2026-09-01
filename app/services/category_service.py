from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, payload: CategoryCreate) -> Category:
    existing = db.query(Category).filter(Category.slug == payload.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this slug already exists",
        )

    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category_by_public_id(db: Session, public_id: str) -> Category:
    category = db.query(Category).filter(Category.public_id == public_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return category


def list_categories(db: Session, skip: int = 0, limit: int = 20, only_active: bool = False):
    query = db.query(Category)
    if only_active:
        query = query.filter(Category.is_active == True)
    return query.offset(skip).limit(limit).all()


def update_category(db: Session, public_id: str, payload: CategoryUpdate) -> Category:
    category = get_category_by_public_id(db, public_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != category.slug:
        existing = db.query(Category).filter(Category.slug == update_data["slug"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this slug already exists",
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, public_id: str) -> None:
    category = get_category_by_public_id(db, public_id)

    if category.tours:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a category with existing tours. Deactivate it instead.",
        )

    db.delete(category)
    db.commit()