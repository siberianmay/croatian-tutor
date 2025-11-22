from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Word(Base):
    """Word model for Croatian vocabulary entries."""

    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    croatian: Mapped[str] = mapped_column(String(200), index=True)
    english: Mapped[str] = mapped_column(String(200), index=True)
    pronunciation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-5 scale
    topic_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("topics.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="words")
    exercises: Mapped[list["Exercise"]] = relationship("Exercise", back_populates="word")
