"""Word API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_language
from app.crud.language import LanguageCRUD
from app.crud.word import WordCRUD
from app.database import get_db
from app.models.enums import CEFRLevel, PartOfSpeech
from app.models.user import User
from app.schemas.word import (
    WordBulkImportRequest,
    WordBulkImportResponse,
    WordCreate,
    WordResponse,
    WordReviewRequest,
    WordReviewResponse,
    WordUpdate,
)
from app.services.gemini_service import get_gemini_service

router = APIRouter(prefix="/words", tags=["words"])


def get_word_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> WordCRUD:
    """Dependency for WordCRUD."""
    return WordCRUD(db)


@router.get("", response_model=list[WordResponse])
async def list_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    part_of_speech: PartOfSpeech | None = None,
    cefr_level: CEFRLevel | None = None,
    search: str | None = Query(None, min_length=1),
    sort_by: str | None = Query(None, pattern="^(croatian|english|part_of_speech|cefr_level|mastery_score|created_at)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
) -> list[WordResponse]:
    """List words with pagination, filters, and sorting."""
    words = await crud.get_multi(
        user_id=current_user.id,
        language=language,
        skip=skip,
        limit=limit,
        part_of_speech=part_of_speech,
        cefr_level=cefr_level,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return [WordResponse.model_validate(w) for w in words]


@router.get("/count")
async def count_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    part_of_speech: PartOfSpeech | None = None,
    cefr_level: CEFRLevel | None = None,
    search: str | None = Query(None, min_length=1),
) -> dict[str, int]:
    """Get total count of words matching filters."""
    count = await crud.count(
        user_id=current_user.id,
        language=language,
        part_of_speech=part_of_speech,
        cefr_level=cefr_level,
        search=search,
    )
    return {"count": count}


@router.get("/due", response_model=list[WordResponse])
async def get_due_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    limit: int = Query(20, ge=1, le=100),
) -> list[WordResponse]:
    """Get words due for review."""
    words = await crud.get_due_words(
        user_id=current_user.id, language=language, limit=limit
    )
    return [WordResponse.model_validate(w) for w in words]


@router.get("/due/count")
async def count_due_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> dict[str, int]:
    """Get count of words due for review."""
    count = await crud.count_due_words(user_id=current_user.id, language=language)
    return {"count": count}


@router.post("", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
async def create_word(
    word_in: WordCreate,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> WordResponse:
    """Create a new word."""
    # Check for duplicates within the same language
    exists = await crud.exists_for_user(
        current_user.id, word_in.croatian, language=language
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Word '{word_in.croatian}' already exists",
        )

    word = await crud.create(user_id=current_user.id, word_in=word_in, language=language)
    return WordResponse.model_validate(word)


@router.get("/{word_id}", response_model=WordResponse)
async def get_word(
    word_id: int,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WordResponse:
    """Get a specific word by ID."""
    word = await crud.get(word_id, user_id=current_user.id)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found",
        )
    return WordResponse.model_validate(word)


@router.put("/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: int,
    word_in: WordUpdate,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WordResponse:
    """Update a word."""
    word = await crud.update(word_id, user_id=current_user.id, word_in=word_in)
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found",
        )
    return WordResponse.model_validate(word)


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_word(
    word_id: int,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """Delete a word."""
    deleted = await crud.delete(word_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found",
        )


@router.post("/{word_id}/review", response_model=WordReviewResponse)
async def review_word(
    word_id: int,
    review_in: WordReviewRequest,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WordReviewResponse:
    """Submit a drill review result and update SRS scheduling."""
    word = await crud.process_review(
        word_id, user_id=current_user.id, correct=review_in.correct
    )
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found",
        )
    return WordReviewResponse(
        word_id=word.id,
        new_mastery_score=word.mastery_score,
        next_review_at=word.next_review_at,
        correct_count=word.correct_count,
        wrong_count=word.wrong_count,
    )


@router.post("/bulk-import", response_model=WordBulkImportResponse)
async def bulk_import_words(
    request: WordBulkImportRequest,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    language: Annotated[str, Depends(get_current_language)],
) -> WordBulkImportResponse:
    """
    Bulk import words with AI-powered assessment.

    Gemini analyzes each word to determine:
    - English translation
    - Part of speech
    - Gender (for nouns)
    - CEFR difficulty level
    """
    gemini = get_gemini_service()
    language_crud = LanguageCRUD(db)

    # Get language name for Gemini prompts
    lang = await language_crud.get(language)
    language_name = lang.name if lang else "Croatian"

    # Filter out duplicates within the same language
    new_words = []
    skipped = 0
    for word in request.words:
        word = word.strip()
        if not word:
            continue
        exists = await crud.exists_for_user(current_user.id, word, language=language)
        if exists:
            skipped += 1
        else:
            new_words.append(word)

    if not new_words:
        return WordBulkImportResponse(
            imported=0,
            skipped_duplicates=skipped,
            words=[],
        )

    # Assess words with Gemini
    assessments = await gemini.assess_words_bulk(new_words, language_name)

    # Create words in database
    created_words = []
    for assessment in assessments:
        if not assessment.get("english"):
            # Skip words that couldn't be assessed
            continue

        word_create = WordCreate(
            croatian=assessment["word"],
            english=assessment["english"],
            part_of_speech=PartOfSpeech(assessment["part_of_speech"]),
            gender=assessment.get("gender"),
            cefr_level=CEFRLevel(assessment["cefr_level"]),
        )
        word = await crud.create(
            user_id=current_user.id, word_in=word_create, language=language
        )
        created_words.append(WordResponse.model_validate(word))

    return WordBulkImportResponse(
        imported=len(created_words),
        skipped_duplicates=skipped,
        words=created_words,
    )
