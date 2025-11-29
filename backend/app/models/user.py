"""User model for the Croatian Tutor application."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import CEFRLevel

if TYPE_CHECKING:
    from app.models.error_log import ErrorLog
    from app.models.exercise_log import ExerciseLog
    from app.models.language import Language
    from app.models.session import Session
    from app.models.topic_progress import TopicProgress
    from app.models.word import Word


class User(Base):
    """User model - single user for local app, extensible for future multi-user."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_cefr_level: Mapped[CEFRLevel] = mapped_column(
        default=CEFRLevel.A1,
        nullable=False,
    )
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    language: Mapped[str] = mapped_column(
        String(8), ForeignKey("language.code"), nullable=False, server_default="hr"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    words: Mapped[list["Word"]] = relationship(back_populates="user", lazy="selectin")
    topic_progress: Mapped[list["TopicProgress"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    exercise_logs: Mapped[list["ExerciseLog"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    error_logs: Mapped[list["ErrorLog"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    selected_language: Mapped["Language"] = relationship(back_populates="users")
