"""Word API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.word import WordCRUD
from app.database import get_db
from app.models.enums import CEFRLevel, PartOfSpeech
from app.schemas.word import (
    WordCreate,
    WordResponse,
    WordReviewRequest,
    WordReviewResponse,
    WordUpdate,
)

router = APIRouter(prefix="/words", tags=["words"])

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_word_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> WordCRUD:
    """Dependency for WordCRUD."""
    return WordCRUD(db)


@router.get("", response_model=list[WordResponse])
async def list_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    part_of_speech: PartOfSpeech | None = None,
    cefr_level: CEFRLevel | None = None,
    search: str | None = Query(None, min_length=1),
) -> list[WordResponse]:
    """List words with pagination and optional filters."""
    words = await crud.get_multi(
        user_id=DEFAULT_USER_ID,
        skip=skip,
        limit=limit,
        part_of_speech=part_of_speech,
        cefr_level=cefr_level,
        search=search,
    )
    return [WordResponse.model_validate(w) for w in words]


@router.get("/count")
async def count_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    part_of_speech: PartOfSpeech | None = None,
    cefr_level: CEFRLevel | None = None,
    search: str | None = Query(None, min_length=1),
) -> dict[str, int]:
    """Get total count of words matching filters."""
    count = await crud.count(
        user_id=DEFAULT_USER_ID,
        part_of_speech=part_of_speech,
        cefr_level=cefr_level,
        search=search,
    )
    return {"count": count}


@router.get("/due", response_model=list[WordResponse])
async def get_due_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
    limit: int = Query(20, ge=1, le=100),
) -> list[WordResponse]:
    """Get words due for review."""
    words = await crud.get_due_words(user_id=DEFAULT_USER_ID, limit=limit)
    return [WordResponse.model_validate(w) for w in words]


@router.get("/due/count")
async def count_due_words(
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
) -> dict[str, int]:
    """Get count of words due for review."""
    count = await crud.count_due_words(user_id=DEFAULT_USER_ID)
    return {"count": count}


@router.post("", response_model=WordResponse, status_code=status.HTTP_201_CREATED)
async def create_word(
    word_in: WordCreate,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
) -> WordResponse:
    """Create a new word."""
    # Check for duplicates
    exists = await crud.exists_for_user(DEFAULT_USER_ID, word_in.croatian)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Word '{word_in.croatian}' already exists",
        )

    word = await crud.create(user_id=DEFAULT_USER_ID, word_in=word_in)
    return WordResponse.model_validate(word)


@router.get("/{word_id}", response_model=WordResponse)
async def get_word(
    word_id: int,
    crud: Annotated[WordCRUD, Depends(get_word_crud)],
) -> WordResponse:
    """Get a specific word by ID."""
    word = await crud.get(word_id, user_id=DEFAULT_USER_ID)
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
) -> WordResponse:
    """Update a word."""
    word = await crud.update(word_id, user_id=DEFAULT_USER_ID, word_in=word_in)
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
) -> None:
    """Delete a word."""
    deleted = await crud.delete(word_id, user_id=DEFAULT_USER_ID)
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
) -> WordReviewResponse:
    """Submit a drill review result and update SRS scheduling."""
    word = await crud.process_review(
        word_id, user_id=DEFAULT_USER_ID, correct=review_in.correct
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
