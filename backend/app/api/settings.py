"""Settings API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.app_settings import AppSettingsCRUD
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdate, VALID_GEMINI_MODELS

router = APIRouter(prefix="/settings", tags=["settings"])


def get_settings_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> AppSettingsCRUD:
    """Dependency for AppSettingsCRUD."""
    return AppSettingsCRUD(db)


@router.get("", response_model=AppSettingsResponse)
async def get_settings(
    crud: Annotated[AppSettingsCRUD, Depends(get_settings_crud)],
) -> AppSettingsResponse:
    """
    Get current application settings.

    Returns all configurable settings including:
    - grammar_batch_size: Number of grammar exercises per batch
    - translation_batch_size: Number of translation exercises per batch
    - reading_passage_length: Approximate passage length in characters
    - gemini_model: AI model used for generation
    """
    settings = await crud.get()
    return AppSettingsResponse.model_validate(settings)


@router.patch("", response_model=AppSettingsResponse)
async def update_settings(
    settings_in: AppSettingsUpdate,
    crud: Annotated[AppSettingsCRUD, Depends(get_settings_crud)],
) -> AppSettingsResponse:
    """
    Update application settings.

    Partial update - only provided fields will be updated.

    Validation:
    - grammar_batch_size: 5-20
    - translation_batch_size: 5-20
    - reading_passage_length: 100-1000
    - gemini_model: Must be a valid Gemini model name
    """
    settings = await crud.update(settings_in)
    return AppSettingsResponse.model_validate(settings)


@router.get("/models", response_model=list[str])
async def get_available_models() -> list[str]:
    """
    Get list of available Gemini models.

    Returns the model names that can be used in the gemini_model setting.
    """
    return VALID_GEMINI_MODELS
