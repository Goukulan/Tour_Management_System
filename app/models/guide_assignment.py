from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.db import Base


class GuideAssignment(Base):
    __tablename__ = "guide_assignments"

    __table_args__ = (
        UniqueConstraint("guide_id", "departure_id", name="uix_guide_departure"),
    )

    id            = Column(Integer, primary_key=True, index=True)

    guide_id      = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    departure_id  = Column(Integer, ForeignKey("departures.id", ondelete="CASCADE"), nullable=False, index=True)

    assigned_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    guide         = relationship("User", backref="guide_assignments")
    departure     = relationship("Departure", backref="guide_assignments")

    def __repr__(self) -> str:
        return f"<GuideAssignment guide_id={self.guide_id} departure_id={self.departure_id}>"