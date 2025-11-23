"""Analytics API endpoints for advanced SRS metrics and learning insights."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Hardcoded user ID for single-user mode
USER_ID = 1


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    """Dependency for analytics service."""
    return AnalyticsService(db)


@router.get("/leeches")
async def get_leeches(
    limit: int = 20,
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """
    Get leech words - words with high failure rates.

    Leeches are words that consistently fail reviews and waste study time.
    Consider special attention or mnemonic techniques for these words.

    Args:
        limit: Maximum number of leeches to return (default 20)
    """
    return await service.get_leeches(USER_ID, limit=limit)


@router.get("/forecast")
async def get_review_forecast(
    days: int = 7,
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """
    Get upcoming review forecast.

    Shows how many words are due for review each day, helping plan study time.

    Args:
        days: Number of days to forecast (default 7)
    """
    return await service.get_review_forecast(USER_ID, days=days)


@router.get("/velocity")
async def get_learning_velocity(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """
    Get learning velocity metrics.

    Shows words added/mastered per week, retention rate, and trend direction.
    """
    return await service.get_learning_velocity(USER_ID)


@router.get("/difficulty")
async def get_difficulty_breakdown(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """
    Get difficulty breakdown by word characteristics.

    Shows performance by part of speech and CEFR level to identify weak areas.
    """
    return await service.get_difficulty_breakdown(USER_ID)


@router.get("/")
async def get_full_analytics(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict[str, Any]:
    """
    Get all analytics in one call.

    Returns leeches, forecast, velocity, and difficulty breakdown.
    """
    return await service.get_full_analytics(USER_ID)
