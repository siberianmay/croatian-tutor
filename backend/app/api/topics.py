"""Grammar Topics API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.grammar_topic import GrammarTopicCRUD, TopicProgressCRUD
from app.database import get_db
from app.models.enums import CEFRLevel
from app.schemas.grammar_topic import (
    GrammarTopicCreate,
    GrammarTopicResponse,
    GrammarTopicUpdate,
    TopicProgressResponse,
)
from app.services.gemini_service import get_gemini_service
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/topics", tags=["grammar-topics"])

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_topic_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> GrammarTopicCRUD:
    """Dependency for GrammarTopicCRUD."""
    return GrammarTopicCRUD(db)


def get_progress_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> TopicProgressCRUD:
    """Dependency for TopicProgressCRUD."""
    return TopicProgressCRUD(db)


def get_exercise_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ExerciseService:
    """Dependency for ExerciseService."""
    return ExerciseService(db, get_gemini_service())


@router.get("", response_model=list[GrammarTopicResponse])
async def list_topics(
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cefr_level: CEFRLevel | None = None,
) -> list[GrammarTopicResponse]:
    """List grammar topics with pagination and optional CEFR level filter."""
    topics = await crud.get_multi(skip=skip, limit=limit, cefr_level=cefr_level)
    return [GrammarTopicResponse.model_validate(t) for t in topics]


@router.get("/count")
async def count_topics(
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    cefr_level: CEFRLevel | None = None,
) -> dict[str, int]:
    """Get total count of topics."""
    count = await crud.count(cefr_level=cefr_level)
    return {"count": count}


@router.get("/progress", response_model=list[TopicProgressResponse])
async def get_user_progress(
    topic_crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    cefr_level: CEFRLevel | None = None,
) -> list[TopicProgressResponse]:
    """Get user's progress on all practiced topics."""
    progress_records = await progress_crud.get_user_progress(
        user_id=DEFAULT_USER_ID, cefr_level=cefr_level
    )

    results = []
    for progress in progress_records:
        topic = await topic_crud.get(progress.topic_id)
        if topic:
            results.append(
                TopicProgressResponse(
                    topic_id=progress.topic_id,
                    topic_name=topic.name,
                    cefr_level=topic.cefr_level,
                    mastery_score=progress.mastery_score,
                    times_practiced=progress.times_practiced,
                )
            )
    return results


@router.post("", response_model=GrammarTopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_in: GrammarTopicCreate,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
) -> GrammarTopicResponse:
    """Create a new grammar topic."""
    # Check for duplicates
    existing = await crud.get_by_name(topic_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Topic '{topic_in.name}' already exists",
        )

    topic = await crud.create(topic_in)
    return GrammarTopicResponse.model_validate(topic)


@router.get("/{topic_id}", response_model=GrammarTopicResponse)
async def get_topic(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
) -> GrammarTopicResponse:
    """Get a specific grammar topic by ID."""
    topic = await crud.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    return GrammarTopicResponse.model_validate(topic)


@router.put("/{topic_id}", response_model=GrammarTopicResponse)
async def update_topic(
    topic_id: int,
    topic_in: GrammarTopicUpdate,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
) -> GrammarTopicResponse:
    """Update a grammar topic."""
    topic = await crud.update(topic_id, topic_in)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    return GrammarTopicResponse.model_validate(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
) -> None:
    """Delete a grammar topic."""
    deleted = await crud.delete(topic_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )


@router.post("/{topic_id}/generate-description", response_model=GrammarTopicResponse)
async def generate_topic_description(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    exercise_service: Annotated[ExerciseService, Depends(get_exercise_service)],
) -> GrammarTopicResponse:
    """Generate AI description for a grammar topic using Gemini."""
    topic = await crud.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    description = await exercise_service.generate_topic_description(topic_id)
    if not description:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate description",
        )

    # Refresh topic from DB
    topic = await crud.get(topic_id)
    return GrammarTopicResponse.model_validate(topic)
