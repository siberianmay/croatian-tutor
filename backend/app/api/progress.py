"""Progress API endpoints for dashboard statistics."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.progress_service import ProgressService

router = APIRouter(prefix="/progress", tags=["progress"])

# Hardcoded user ID for single-user mode
USER_ID = 1


def get_progress_service(db: AsyncSession = Depends(get_db)) -> ProgressService:
    """Dependency for progress service."""
    return ProgressService(db)


@router.get("/summary")
async def get_summary(
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, Any]:
    """
    Get overall learning summary.

    Returns stats like total words, mastered words, streak days, etc.
    """
    return await service.get_summary(USER_ID)


@router.get("/vocabulary")
async def get_vocabulary_stats(
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, Any]:
    """
    Get vocabulary breakdown.

    Returns words by level, by mastery status, and recent additions.
    """
    return await service.get_vocabulary_stats(USER_ID)


@router.get("/topics")
async def get_topic_stats(
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, Any]:
    """
    Get grammar topic progress.

    Returns topic mastery levels and practice counts.
    """
    return await service.get_topic_stats(USER_ID)


@router.get("/activity")
async def get_activity(
    days: int = 14,
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, Any]:
    """
    Get recent activity timeline.

    Args:
        days: Number of days to include (default 14)

    Returns daily activity and exercise type breakdown.
    """
    return await service.get_activity(USER_ID, days=days)


@router.get("/errors")
async def get_error_patterns(
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, Any]:
    """
    Get error patterns and weak areas.

    Returns error distribution by category and suggestions for improvement.
    """
    return await service.get_error_patterns(USER_ID)


@router.get("/context")
async def get_context_summary(
    service: ProgressService = Depends(get_progress_service),
) -> dict[str, str]:
    """
    Get a text summary for AI context.

    Returns a formatted summary suitable for Gemini prompts.
    """
    summary = await service.generate_context_summary(USER_ID)
    return {"context": summary}
