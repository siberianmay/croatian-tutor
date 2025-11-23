"""Pydantic schemas for sessions."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ExerciseType


class SessionCreate(BaseModel):
    """Schema for creating a new session."""

    exercise_type: ExerciseType


class SessionEnd(BaseModel):
    """Schema for ending a session."""

    outcome: str | None = Field(None, max_length=500)


class SessionResponse(BaseModel):
    """Schema for session response."""

    id: int
    user_id: int
    started_at: datetime
    ended_at: datetime | None
    exercise_type: ExerciseType
    duration_minutes: int
    outcome: str | None

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    """Schema for listing sessions."""

    sessions: list[SessionResponse]
    total: int
