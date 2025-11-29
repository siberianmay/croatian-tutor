"""Grammar topic model for the Croatian Tutor application."""

from typing import TYPE_CHECKING

from sqlalchemy import ARRAY, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import CEFRLevel

if TYPE_CHECKING:
    from app.models.error_log import ErrorLog
    from app.models.language import Language
    from app.models.topic_progress import TopicProgress


class GrammarTopic(Base):
    """Grammar topic definitions with rule descriptions."""

    __tablename__ = "grammar_topic"
    __table_args__ = (
        UniqueConstraint("name", "language", name="uq_grammar_topic_name_language"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    language: Mapped[str] = mapped_column(
        String(8), ForeignKey("language.code"), nullable=False, index=True, server_default="hr"
    )
    cefr_level: Mapped[CEFRLevel] = mapped_column(nullable=False)
    prerequisite_ids: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer), nullable=True
    )
    rule_description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Markdown, Gemini-generated
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    language_ref: Mapped["Language"] = relationship(back_populates="grammar_topics")
    progress_records: Mapped[list["TopicProgress"]] = relationship(
        back_populates="topic", lazy="selectin"
    )
    error_logs: Mapped[list["ErrorLog"]] = relationship(
        back_populates="topic", lazy="selectin"
    )
