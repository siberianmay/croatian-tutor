"""Pydantic schemas for Language model."""

from datetime import datetime

from pydantic import BaseModel, Field


class LanguageBase(BaseModel):
    """Base schema for language data."""

    code: str = Field(..., min_length=2, max_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    native_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class LanguageCreate(LanguageBase):
    """Schema for creating a language."""

    pass
