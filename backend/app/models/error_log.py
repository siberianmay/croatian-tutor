"""Error log model for the Croatian Tutor application."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ErrorCategory

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.grammar_topic import GrammarTopic


class ErrorLog(Base):
    """Categorized error tracking for pattern analysis."""

    __tablename__ = "error_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    error_category: Mapped[ErrorCategory] = mapped_column(nullable=False)
    topic_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("grammar_topic.id"), nullable=True, index=True
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # The actual mistake
    correction: Mapped[str | None] = mapped_column(Text, nullable=True)  # Correct form

    # Relationships
    user: Mapped["User"] = relationship(back_populates="error_logs")
    topic: Mapped["GrammarTopic | None"] = relationship(back_populates="error_logs")
