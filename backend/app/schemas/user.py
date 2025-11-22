"""Pydantic schemas for User model."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CEFRLevel


class UserBase(BaseModel):
    """Base schema for user data."""

    name: str | None = Field(None, max_length=100)
    preferred_cefr_level: CEFRLevel = CEFRLevel.A1
    daily_goal_minutes: int = Field(30, ge=0, le=480)


class UserUpdate(UserBase):
    """Schema for updating user settings."""

    pass


class UserResponse(UserBase):
    """Schema for user response data."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
