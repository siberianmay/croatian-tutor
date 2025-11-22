"""Pydantic schemas for vocabulary drills."""

from pydantic import BaseModel, Field

from app.models.enums import ExerciseType


class DrillItem(BaseModel):
    """A single drill item."""

    word_id: int
    prompt: str
    expected_answer: str
    part_of_speech: str
    gender: str | None = None
    cefr_level: str | None = None


class DrillSessionRequest(BaseModel):
    """Request to start a drill session."""

    exercise_type: ExerciseType = Field(
        ...,
        description="Type of drill (vocabulary_cr_en or vocabulary_en_cr)",
    )
    count: int = Field(10, ge=1, le=50, description="Number of words to drill")


class DrillSessionResponse(BaseModel):
    """Response with drill items for a session."""

    exercise_type: ExerciseType
    items: list[DrillItem]
    total_count: int


class DrillAnswerRequest(BaseModel):
    """Request to check a drill answer."""

    word_id: int
    user_answer: str = Field(..., min_length=1)
    exercise_type: ExerciseType


class DrillAnswerResponse(BaseModel):
    """Response after checking a drill answer."""

    correct: bool
    expected_answer: str
    user_answer: str
    word_id: int


class FillInBlankItem(BaseModel):
    """A fill-in-the-blank exercise item."""

    word_id: int
    sentence: str  # Sentence with ___ placeholder
    answer: str  # The word that fills the blank
    hint: str  # English hint


class FillInBlankRequest(BaseModel):
    """Request to get fill-in-blank exercises."""

    count: int = Field(5, ge=1, le=20, description="Number of exercises to generate")
