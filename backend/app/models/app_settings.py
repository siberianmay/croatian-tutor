"""Application settings model for the Croatian Tutor application."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AppSettings(Base):
    """
    Singleton settings table (id=1 always).

    Stores application-wide configuration for exercise generation
    and AI model selection.
    """

    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)

    # Exercise batch sizes
    grammar_batch_size: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
        comment="Number of grammar exercises per batch (5-20)"
    )
    translation_batch_size: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
        comment="Number of translation exercises per batch (5-20)"
    )

    # Reading comprehension settings
    reading_passage_length: Mapped[int] = mapped_column(
        Integer,
        default=350,
        nullable=False,
        comment="Approximate passage length in characters (100-1000)"
    )

    # AI model selection
    gemini_model: Mapped[str] = mapped_column(
        String(50),
        default="gemini-2.5-flash",
        nullable=False,
        comment="Gemini model to use for AI generation"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
