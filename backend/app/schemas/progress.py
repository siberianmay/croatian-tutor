"""Pydantic schemas for progress and statistics."""

from datetime import date, datetime

from pydantic import BaseModel

from app.models.enums import CEFRLevel, ErrorCategory, ExerciseType


class VocabularyStats(BaseModel):
    """Statistics about vocabulary."""

    total_words: int
    strong_count: int  # mastery 8-10
    medium_count: int  # mastery 4-7
    weak_count: int  # mastery 0-3
    due_for_review: int
    by_cefr_level: dict[CEFRLevel, int]


class TopicMasteryStats(BaseModel):
    """Statistics about topic mastery."""

    completed: list[dict]  # [{name, score}] - score >= 8
    in_progress: list[dict]  # [{name, score}] - score 1-7
    not_started: list[str]  # topic names with score 0


class ExerciseActivityStats(BaseModel):
    """Exercise activity over a time period."""

    period_days: int
    total_minutes: int
    by_exercise_type: dict[ExerciseType, int]  # minutes per type


class ErrorPatternStats(BaseModel):
    """Error patterns over a time period."""

    period_days: int
    total_errors: int
    by_category: dict[ErrorCategory, int]
    improving: list[str]  # categories with decreasing errors
    frequent: list[str]  # most common error categories


class ProgressSummary(BaseModel):
    """Overall progress summary for dashboard."""

    vocabulary: VocabularyStats
    topics: TopicMasteryStats
    recent_activity: ExerciseActivityStats
    error_patterns: ErrorPatternStats
    estimated_cefr: CEFRLevel


class DailyActivity(BaseModel):
    """Daily activity record."""

    date: date
    exercise_type: ExerciseType
    duration_minutes: int
    exercises_completed: int


class SessionRecord(BaseModel):
    """Session history record."""

    id: int
    started_at: datetime
    ended_at: datetime | None
    exercise_type: ExerciseType
    duration_minutes: int
    outcome: str | None

    model_config = {"from_attributes": True}
