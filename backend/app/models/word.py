"""Word model for the Croatian Tutor application."""

from datetime import datetime
from typing import TYPE_CHECKING

from app.database import Base
from app.models.enums import CEFRLevel, Gender, PartOfSpeech
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class Word(Base):
    """Vocabulary word with SRS (Spaced Repetition System) fields."""

    __tablename__ = "word"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Word content
    croatian: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    english: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # Linguistic properties
    part_of_speech: Mapped[PartOfSpeech] = mapped_column(nullable=False)
    gender: Mapped[Gender | None] = mapped_column(nullable=True)  # Only for nouns
    cefr_level: Mapped[CEFRLevel] = mapped_column(nullable=False)

    # SRS fields
    mastery_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-10
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)  # SM-2
    correct_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Consecutive correct
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="words")

    def __str__(self):
        return self.croatian

    def __repr__(self):
        return self.__str__()
