"""Pydantic schemas for exercises."""

from pydantic import BaseModel, Field

from app.models.enums import CEFRLevel, ExerciseType


class ExerciseRequest(BaseModel):
    """Base request for generating an exercise."""

    exercise_type: ExerciseType
    cefr_level: CEFRLevel | None = None  # If None, use user's preferred level


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""

    role: str  # "user" or "assistant"
    content: str


class ConversationRequest(BaseModel):
    """Request for a conversation turn with the tutor."""

    message: str = Field(..., min_length=1)
    history: list[ConversationTurn] = []


class ConversationResponse(BaseModel):
    """Response from conversation with tutor."""

    response: str
    corrections: list[dict] | None = None  # [{original, corrected, explanation}]
    new_vocabulary: list[str] | None = None  # Words to potentially add


class GrammarExerciseRequest(BaseModel):
    """Request for a grammar exercise."""

    topic_id: int | None = None  # If None, auto-select based on progress


class GrammarExerciseResponse(BaseModel):
    """Response with a grammar exercise."""

    exercise_id: str
    topic_id: int
    topic_name: str
    instruction: str
    question: str
    hints: list[str] | None = None


class TranslationRequest(BaseModel):
    """Request for a translation exercise."""

    direction: str = Field(..., pattern="^(cr_en|en_cr)$")  # Croatian to English or vice versa
    cefr_level: CEFRLevel | None = None
    recent_sentences: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Recent sentences to avoid repetition",
    )


class TranslationResponse(BaseModel):
    """Response with a translation exercise."""

    exercise_id: str
    source_text: str
    source_language: str
    target_language: str
    expected_answer: str


class ExerciseEvaluationRequest(BaseModel):
    """Request to evaluate an exercise answer."""

    exercise_id: str
    exercise_type: ExerciseType
    answer: str


class ExerciseEvaluationResponse(BaseModel):
    """Response with evaluation of an exercise."""

    correct: bool
    score: float  # 0.0 - 1.0
    feedback: str
    correct_answer: str | None = None
    error_category: str | None = None  # For tracking
    explanation: str | None = None


class FillInBlankExercise(BaseModel):
    """Fill-in-the-blank exercise data."""

    exercise_id: str
    sentence_with_blank: str  # "Ja ___ u školu." (I go to school)
    word_to_practice: str  # The Croatian word being tested
    hint: str | None = None
