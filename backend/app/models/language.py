"""Language model for multi-language support."""

from datetime import datetime
from typing import TYPE_CHECKING

from app.database import Base
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.error_log import ErrorLog
    from app.models.exercise_log import ExerciseLog
    from app.models.grammar_topic import GrammarTopic
    from app.models.session import Session
    from app.models.user import User
    from app.models.word import Word


class Language(Base):
    """Language model for managing supported learning languages."""

    __tablename__ = "language"

    code: Mapped[str] = mapped_column(String(8), primary_key=True, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    words: Mapped[list["Word"]] = relationship(back_populates="language_ref", lazy="selectin")
    grammar_topics: Mapped[list["GrammarTopic"]] = relationship(back_populates="language_ref", lazy="selectin")
    sessions: Mapped[list["Session"]] = relationship(back_populates="language_ref", lazy="selectin")
    exercise_logs: Mapped[list["ExerciseLog"]] = relationship(back_populates="language_ref", lazy="selectin")
    error_logs: Mapped[list["ErrorLog"]] = relationship(back_populates="language_ref", lazy="selectin")
    users: Mapped[list["User"]] = relationship(back_populates="selected_language", lazy="selectin")
