"""Analytics API endpoints for advanced SRS metrics and learning insights."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_language
from app.database import get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AnalyticsService:
    """Dependency for analytics service."""
    return AnalyticsService(db)


@router.get("/leeches")
async def get_leeches(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    limit: int = 20,
) -> dict[str, Any]:
    """
    Get leech words - words with high failure rates.

    Leeches are words that consistently fail reviews and waste study time.
    Consider special attention or mnemonic techniques for these words.

    Args:
        limit: Maximum number of leeches to return (default 20)
    """
    return await service.get_leeches(current_user.id, language, limit=limit)


@router.get("/forecast")
async def get_review_forecast(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    days: int = 7,
) -> dict[str, Any]:
    """
    Get upcoming review forecast.

    Shows how many words are due for review each day, helping plan study time.

    Args:
        days: Number of days to forecast (default 7)
    """
    return await service.get_review_forecast(current_user.id, language, days=days)


@router.get("/velocity")
async def get_learning_velocity(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> dict[str, Any]:
    """
    Get learning velocity metrics.

    Shows words added/mastered per week, retention rate, and trend direction.
    """
    return await service.get_learning_velocity(current_user.id, language)


@router.get("/difficulty")
async def get_difficulty_breakdown(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> dict[str, Any]:
    """
    Get difficulty breakdown by word characteristics.

    Shows performance by part of speech and CEFR level to identify weak areas.
    """
    return await service.get_difficulty_breakdown(current_user.id, language)


@router.get("/")
async def get_full_analytics(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> dict[str, Any]:
    """
    Get all analytics in one call.

    Returns leeches, forecast, velocity, and difficulty breakdown.
    """
    return await service.get_full_analytics(current_user.id, language)
