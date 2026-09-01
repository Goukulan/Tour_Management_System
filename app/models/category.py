from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func

from app.core.db import Base
from app.utils.security import generate_short_id


class Category(Base):
    __tablename__ = "categories"

    id           = Column(Integer, primary_key=True, index=True)
    public_id    = Column(String(10), unique=True, default=lambda: generate_short_id(10), index=True, nullable=False)

    name         = Column(String, nullable=False)
    slug         = Column(String, unique=True, index=True, nullable=False)
    description  = Column(Text, nullable=True)
    icon_url     = Column(String, nullable=True)

    is_active    = Column(Boolean, default=True, nullable=False)

    created_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name}>"