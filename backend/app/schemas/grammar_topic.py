"""Pydantic schemas for GrammarTopic model."""

from pydantic import BaseModel, Field

from app.models.enums import CEFRLevel


class GrammarTopicBase(BaseModel):
    """Base schema for grammar topic data."""

    name: str = Field(..., min_length=1, max_length=200)
    cefr_level: CEFRLevel
    prerequisite_ids: list[int] | None = None
    rule_description: str | None = None
    display_order: int = 0


class GrammarTopicCreate(GrammarTopicBase):
    """Schema for creating a grammar topic."""

    pass


class GrammarTopicUpdate(BaseModel):
    """Schema for updating a grammar topic."""

    name: str | None = Field(None, min_length=1, max_length=200)
    cefr_level: CEFRLevel | None = None
    prerequisite_ids: list[int] | None = None
    rule_description: str | None = None
    display_order: int | None = None


class GrammarTopicResponse(GrammarTopicBase):
    """Schema for grammar topic response data."""

    id: int
    language: str  # Language code (e.g., 'hr', 'es')
    is_learnt: bool = False
    mastery_score: int = 0
    times_practiced: int = 0

    model_config = {"from_attributes": True}


class TopicProgressResponse(BaseModel):
    """Schema for user's progress on a topic."""

    topic_id: int
    topic_name: str
    language: str  # Language code (e.g., 'hr', 'es')
    cefr_level: CEFRLevel
    mastery_score: int
    times_practiced: int

    model_config = {"from_attributes": True}
