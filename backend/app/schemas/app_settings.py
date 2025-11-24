"""Pydantic schemas for AppSettings model."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Valid Gemini model names
VALID_GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

GeminiModelType = Literal[
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]


class AppSettingsResponse(BaseModel):
    """Schema for app settings response."""

    grammar_batch_size: int
    translation_batch_size: int
    reading_passage_length: int
    gemini_model: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppSettingsUpdate(BaseModel):
    """Schema for updating app settings (partial update)."""

    grammar_batch_size: int | None = Field(
        None,
        ge=3,
        le=20,
        description="Number of grammar exercises per batch"
    )
    translation_batch_size: int | None = Field(
        None,
        ge=3,
        le=20,
        description="Number of translation exercises per batch"
    )
    reading_passage_length: int | None = Field(
        None,
        ge=100,
        le=1000,
        description="Approximate passage length in characters"
    )
    gemini_model: str | None = Field(
        None,
        description="Gemini model to use for AI generation"
    )

    @field_validator("gemini_model")
    @classmethod
    def validate_gemini_model(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_GEMINI_MODELS:
            raise ValueError(f"Invalid model. Must be one of: {', '.join(VALID_GEMINI_MODELS)}")
        return v
