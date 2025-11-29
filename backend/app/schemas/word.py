"""Pydantic schemas for Word model."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CEFRLevel, Gender, PartOfSpeech


class WordBase(BaseModel):
    """Base schema for word data."""

    croatian: str = Field(..., min_length=1, max_length=200)
    english: str = Field(..., min_length=1, max_length=200)
    part_of_speech: PartOfSpeech
    gender: Gender | None = None
    cefr_level: CEFRLevel


class WordCreate(WordBase):
    """Schema for creating a word."""

    pass


class WordUpdate(BaseModel):
    """Schema for updating a word."""

    croatian: str | None = Field(None, min_length=1, max_length=200)
    english: str | None = Field(None, min_length=1, max_length=200)
    part_of_speech: PartOfSpeech | None = None
    gender: Gender | None = None
    cefr_level: CEFRLevel | None = None


class WordResponse(WordBase):
    """Schema for word response data."""

    id: int
    user_id: int
    language: str  # Language code (e.g., 'hr', 'es')
    mastery_score: int
    ease_factor: float
    correct_count: int
    wrong_count: int
    next_review_at: datetime | None
    last_reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WordBulkImportRequest(BaseModel):
    """Schema for bulk importing Croatian words."""

    words: list[str] = Field(..., min_length=1, description="List of Croatian words")


class WordBulkImportResponse(BaseModel):
    """Schema for bulk import response."""

    imported: int
    skipped_duplicates: int
    words: list[WordResponse]


class WordReviewRequest(BaseModel):
    """Schema for submitting a drill review result."""

    correct: bool
    response_time_ms: int | None = None  # Optional timing data


class WordReviewResponse(BaseModel):
    """Schema for review result with updated SRS data."""

    word_id: int
    new_mastery_score: int
    next_review_at: datetime | None
    correct_count: int
    wrong_count: int
