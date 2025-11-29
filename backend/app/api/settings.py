"""Settings API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_user_crud
from app.crud.language import LanguageCRUD
from app.crud.user import UserCRUD
from app.database import get_db
from app.crud.app_settings import AppSettingsCRUD
from app.models.user import User
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdate, VALID_GEMINI_MODELS
from app.schemas.language import LanguageResponse

router = APIRouter(prefix="/settings", tags=["settings"])


def get_settings_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> AppSettingsCRUD:
    """Dependency for AppSettingsCRUD."""
    return AppSettingsCRUD(db)


def get_language_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> LanguageCRUD:
    """Dependency for LanguageCRUD."""
    return LanguageCRUD(db)


class LanguageSettingResponse(BaseModel):
    """Response for user's language setting."""

    language_code: str
    language: LanguageResponse


class LanguageSettingUpdate(BaseModel):
    """Request to update user's language."""

    language_code: str = Field(..., min_length=2, max_length=8)


@router.get("", response_model=AppSettingsResponse)
async def get_settings(
    crud: Annotated[AppSettingsCRUD, Depends(get_settings_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> AppSettingsResponse:
    """
    Get current application settings.

    Returns all configurable settings including:
    - grammar_batch_size: Number of grammar exercises per batch
    - translation_batch_size: Number of translation exercises per batch
    - reading_passage_length: Approximate passage length in characters
    - gemini_model: AI model used for generation
    """
    settings = await crud.get_or_create(current_user.id)
    return AppSettingsResponse.model_validate(settings)


@router.patch("", response_model=AppSettingsResponse)
async def update_settings(
    settings_in: AppSettingsUpdate,
    crud: Annotated[AppSettingsCRUD, Depends(get_settings_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
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
    settings = await crud.update(current_user.id, settings_in)
    return AppSettingsResponse.model_validate(settings)


@router.get("/models", response_model=list[str])
async def get_available_models() -> list[str]:
    """
    Get list of available Gemini models.

    Returns the model names that can be used in the gemini_model setting.
    """
    return VALID_GEMINI_MODELS


@router.get("/language", response_model=LanguageSettingResponse)
async def get_user_language(
    current_user: Annotated[User, Depends(get_current_active_user)],
    language_crud: Annotated[LanguageCRUD, Depends(get_language_crud)],
) -> LanguageSettingResponse:
    """
    Get user's current learning language.

    Returns the language code and full language details.
    """
    language_code = current_user.language
    language = await language_crud.get(language_code)

    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{language_code}' not found",
        )

    return LanguageSettingResponse(
        language_code=language_code,
        language=LanguageResponse.model_validate(language),
    )


@router.patch("/language", response_model=LanguageSettingResponse)
async def set_user_language(
    settings_in: LanguageSettingUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
    language_crud: Annotated[LanguageCRUD, Depends(get_language_crud)],
) -> LanguageSettingResponse:
    """
    Set user's learning language.

    Changes the language used for all vocabulary, exercises, and progress tracking.
    """
    # Verify language exists and is active
    language = await language_crud.get(settings_in.language_code)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{settings_in.language_code}' not found",
        )
    if not language.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language '{settings_in.language_code}' is not active",
        )

    # Update user's language
    await user_crud.set_language(current_user.id, settings_in.language_code)

    return LanguageSettingResponse(
        language_code=settings_in.language_code,
        language=LanguageResponse.model_validate(language),
    )
