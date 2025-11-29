"""Session model for the Croatian Tutor application."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ExerciseType

if TYPE_CHECKING:
    from app.models.language import Language
    from app.models.user import User


class Session(Base):
    """Exercise session metadata (no full transcripts)."""

    __tablename__ = "session"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(
        String(8), ForeignKey("language.code"), nullable=False, index=True, server_default="hr"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    exercise_type: Mapped[ExerciseType] = mapped_column(nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    outcome: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # Summary/result

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")
    language_ref: Mapped["Language"] = relationship(back_populates="sessions")
