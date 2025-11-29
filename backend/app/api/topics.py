"""Grammar Topics API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_language
from app.crud.grammar_topic import GrammarTopicCRUD, TopicProgressCRUD
from app.database import get_db
from app.models.enums import CEFRLevel
from app.models.user import User
from app.schemas.grammar_topic import (
    GrammarTopicCreate,
    GrammarTopicResponse,
    GrammarTopicUpdate,
    TopicProgressResponse,
)
from app.services.gemini_service import get_gemini_service
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/topics", tags=["grammar-topics"])


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
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    cefr_level: CEFRLevel | None = None,
) -> list[GrammarTopicResponse]:
    """List grammar topics with pagination and optional CEFR level filter."""
    topics = await crud.get_multi(
        language=language, skip=skip, limit=limit, cefr_level=cefr_level
    )
    progress_map = await progress_crud.get_progress_map(current_user.id, language=language)

    return [
        GrammarTopicResponse(
            id=t.id,
            name=t.name,
            language=t.language,
            cefr_level=t.cefr_level,
            prerequisite_ids=t.prerequisite_ids,
            rule_description=t.rule_description,
            display_order=t.display_order,
            is_learnt=t.id in progress_map,
            mastery_score=progress_map[t.id].mastery_score if t.id in progress_map else 0,
            times_practiced=progress_map[t.id].times_practiced if t.id in progress_map else 0,
        )
        for t in topics
    ]


@router.get("/count")
async def count_topics(
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    language: Annotated[str, Depends(get_current_language)],
    cefr_level: CEFRLevel | None = None,
) -> dict[str, int]:
    """Get total count of topics."""
    count = await crud.count(language=language, cefr_level=cefr_level)
    return {"count": count}


@router.get("/progress", response_model=list[TopicProgressResponse])
async def get_user_progress(
    topic_crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    cefr_level: CEFRLevel | None = None,
) -> list[TopicProgressResponse]:
    """Get user's progress on all practiced topics."""
    progress_records = await progress_crud.get_user_progress(
        user_id=current_user.id, language=language, cefr_level=cefr_level
    )

    results = []
    for progress in progress_records:
        topic = await topic_crud.get(progress.topic_id)
        if topic:
            results.append(
                TopicProgressResponse(
                    topic_id=progress.topic_id,
                    topic_name=topic.name,
                    language=topic.language,
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
    language: Annotated[str, Depends(get_current_language)],
) -> GrammarTopicResponse:
    """Create a new grammar topic."""
    # Check for duplicates within the same language
    existing = await crud.get_by_name(topic_in.name, language=language)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Topic '{topic_in.name}' already exists",
        )

    topic = await crud.create(topic_in, language=language)
    return GrammarTopicResponse.model_validate(topic)


@router.get("/{topic_id}", response_model=GrammarTopicResponse)
async def get_topic(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> GrammarTopicResponse:
    """Get a specific grammar topic by ID."""
    topic = await crud.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )
    progress_map = await progress_crud.get_progress_map(current_user.id, language=language)
    progress = progress_map.get(topic_id)
    return GrammarTopicResponse(
        id=topic.id,
        name=topic.name,
        language=topic.language,
        cefr_level=topic.cefr_level,
        prerequisite_ids=topic.prerequisite_ids,
        rule_description=topic.rule_description,
        display_order=topic.display_order,
        is_learnt=topic_id in progress_map,
        mastery_score=progress.mastery_score if progress else 0,
        times_practiced=progress.times_practiced if progress else 0,
    )


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


@router.post("/{topic_id}/mark-learnt", response_model=GrammarTopicResponse)
async def mark_topic_learnt(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> GrammarTopicResponse:
    """Mark a grammar topic as learnt for the current user."""
    topic = await crud.get(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    progress = await progress_crud.mark_as_learnt(current_user.id, topic_id)

    return GrammarTopicResponse(
        id=topic.id,
        language=topic.language,
        name=topic.name,
        cefr_level=topic.cefr_level,
        prerequisite_ids=topic.prerequisite_ids,
        rule_description=topic.rule_description,
        display_order=topic.display_order,
        is_learnt=True,
        mastery_score=progress.mastery_score,
        times_practiced=progress.times_practiced,
    )


@router.post("/{topic_id}/generate-description", response_model=GrammarTopicResponse)
async def generate_topic_description(
    topic_id: int,
    crud: Annotated[GrammarTopicCRUD, Depends(get_topic_crud)],
    progress_crud: Annotated[TopicProgressCRUD, Depends(get_progress_crud)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    exercise_service: Annotated[ExerciseService, Depends(get_exercise_service)],
    language: Annotated[str, Depends(get_current_language)],
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

    progress_map = await progress_crud.get_progress_map(current_user.id, language=language)
    progress = progress_map.get(topic_id)

    # Refresh topic from DB
    topic = await crud.get(topic_id)
    return GrammarTopicResponse(
        id=topic.id,
        name=topic.name,
        language=topic.language,
        cefr_level=topic.cefr_level,
        prerequisite_ids=topic.prerequisite_ids,
        rule_description=topic.rule_description,
        display_order=topic.display_order,
        is_learnt=topic_id in progress_map,
        mastery_score=progress.mastery_score if progress else 0,
        times_practiced=progress.times_practiced if progress else 0,
    )
