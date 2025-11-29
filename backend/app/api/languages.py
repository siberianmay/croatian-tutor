"""Language API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.language import LanguageCRUD
from app.database import get_db
from app.schemas.language import LanguageResponse

router = APIRouter(prefix="/languages", tags=["languages"])


def get_language_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> LanguageCRUD:
    """Dependency for LanguageCRUD."""
    return LanguageCRUD(db)


@router.get("", response_model=list[LanguageResponse])
async def list_languages(
    crud: Annotated[LanguageCRUD, Depends(get_language_crud)],
) -> list[LanguageResponse]:
    """List all active languages available for learning."""
    languages = await crud.get_all_active()
    return [LanguageResponse.model_validate(lang) for lang in languages]


@router.get("/{code}", response_model=LanguageResponse)
async def get_language(
    code: str,
    crud: Annotated[LanguageCRUD, Depends(get_language_crud)],
) -> LanguageResponse:
    """Get a specific language by code."""
    language = await crud.get(code)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language '{code}' not found",
        )
    return LanguageResponse.model_validate(language)
