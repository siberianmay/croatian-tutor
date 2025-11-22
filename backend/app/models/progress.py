from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserProgress(Base):
    """User progress model for tracking overall learning progress."""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, index=True
    )
    total_words_learned: Mapped[int] = mapped_column(Integer, default=0)
    total_exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    topics_completed: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer), nullable=True, default=[]
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress_records")

    @property
    def accuracy_rate(self) -> float:
        """Calculate accuracy rate as percentage."""
        if self.total_exercises_completed == 0:
            return 0.0
        return (self.total_correct_answers / self.total_exercises_completed) * 100
