"""Exercise log model for the Croatian Tutor application."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ExerciseType

if TYPE_CHECKING:
    from app.models.user import User


class ExerciseLog(Base):
    """Daily exercise activity tracking."""

    __tablename__ = "exercise_log"
    __table_args__ = (
        UniqueConstraint("user_id", "date", "exercise_type", name="uq_user_date_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    exercise_type: Mapped[ExerciseType] = mapped_column(nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    exercises_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="exercise_logs")
