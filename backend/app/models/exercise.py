from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ExerciseType(str, Enum):
    """Types of exercises available."""

    TRANSLATION = "translation"
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_BLANK = "fill_blank"
    CONVERSATION = "conversation"


class Exercise(Base):
    """Exercise model for practice questions."""

    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    question: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5 scale
    word_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("words.id"), nullable=True, index=True
    )
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("topics.id"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    word: Mapped["Word | None"] = relationship("Word", back_populates="exercises")
    topic: Mapped["Topic | None"] = relationship("Topic", back_populates="exercises")
    attempts: Mapped[list["ExerciseAttempt"]] = relationship(
        "ExerciseAttempt", back_populates="exercise"
    )
