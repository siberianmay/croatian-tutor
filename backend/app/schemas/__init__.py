"""Pydantic schemas for the Croatian Tutor application."""

from app.schemas.language import LanguageBase, LanguageCreate, LanguageResponse
from app.schemas.user import UserBase, UserUpdate, UserResponse
from app.schemas.word import (
    WordBase,
    WordCreate,
    WordUpdate,
    WordResponse,
    WordBulkImportRequest,
    WordBulkImportResponse,
    WordReviewRequest,
    WordReviewResponse,
)
from app.schemas.grammar_topic import (
    GrammarTopicBase,
    GrammarTopicCreate,
    GrammarTopicUpdate,
    GrammarTopicResponse,
    TopicProgressResponse,
)
from app.schemas.progress import (
    VocabularyStats,
    TopicMasteryStats,
    ExerciseActivityStats,
    ErrorPatternStats,
    ProgressSummary,
    DailyActivity,
    SessionRecord,
)
from app.schemas.exercise import (
    ExerciseRequest,
    ConversationTurn,
    ConversationRequest,
    ConversationResponse,
    GrammarExerciseRequest,
    GrammarExerciseResponse,
    TranslationRequest,
    TranslationResponse,
    ExerciseEvaluationRequest,
    ExerciseEvaluationResponse,
    FillInBlankExercise,
)
from app.schemas.drill import (
    DrillItem,
    DrillSessionRequest,
    DrillSessionResponse,
    DrillAnswerRequest,
    DrillAnswerResponse,
)

__all__ = [
    # Language
    "LanguageBase",
    "LanguageCreate",
    "LanguageResponse",
    # User
    "UserBase",
    "UserUpdate",
    "UserResponse",
    # Word
    "WordBase",
    "WordCreate",
    "WordUpdate",
    "WordResponse",
    "WordBulkImportRequest",
    "WordBulkImportResponse",
    "WordReviewRequest",
    "WordReviewResponse",
    # Grammar Topic
    "GrammarTopicBase",
    "GrammarTopicCreate",
    "GrammarTopicUpdate",
    "GrammarTopicResponse",
    "TopicProgressResponse",
    # Progress
    "VocabularyStats",
    "TopicMasteryStats",
    "ExerciseActivityStats",
    "ErrorPatternStats",
    "ProgressSummary",
    "DailyActivity",
    "SessionRecord",
    # Exercise
    "ExerciseRequest",
    "ConversationTurn",
    "ConversationRequest",
    "ConversationResponse",
    "GrammarExerciseRequest",
    "GrammarExerciseResponse",
    "TranslationRequest",
    "TranslationResponse",
    "ExerciseEvaluationRequest",
    "ExerciseEvaluationResponse",
    "FillInBlankExercise",
    # Drill
    "DrillItem",
    "DrillSessionRequest",
    "DrillSessionResponse",
    "DrillAnswerRequest",
    "DrillAnswerResponse",
]
