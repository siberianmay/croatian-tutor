"""Drill API endpoints for vocabulary practice."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.enums import ExerciseType
from app.schemas.drill import (
    DrillAnswerRequest,
    DrillAnswerResponse,
    DrillItem,
    DrillSessionRequest,
    DrillSessionResponse,
)
from app.services.drill_service import DrillService

router = APIRouter(prefix="/drills", tags=["drills"])

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_drill_service(db: Annotated[AsyncSession, Depends(get_db)]) -> DrillService:
    """Dependency for DrillService."""
    return DrillService(db)


@router.post("/start", response_model=DrillSessionResponse)
async def start_drill_session(
    request: DrillSessionRequest,
    service: Annotated[DrillService, Depends(get_drill_service)],
) -> DrillSessionResponse:
    """Start a new drill session with specified exercise type."""
    if request.exercise_type not in (
        ExerciseType.VOCABULARY_CR_EN,
        ExerciseType.VOCABULARY_EN_CR,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid exercise type. Use vocabulary_cr_en or vocabulary_en_cr",
        )

    if request.exercise_type == ExerciseType.VOCABULARY_CR_EN:
        items_data = await service.get_cr_to_en_drill(
            user_id=DEFAULT_USER_ID,
            count=request.count,
        )
    else:
        items_data = await service.get_en_to_cr_drill(
            user_id=DEFAULT_USER_ID,
            count=request.count,
        )

    items = [DrillItem(**item) for item in items_data]

    return DrillSessionResponse(
        exercise_type=request.exercise_type,
        items=items,
        total_count=len(items),
    )


@router.post("/check", response_model=DrillAnswerResponse)
async def check_drill_answer(
    request: DrillAnswerRequest,
    service: Annotated[DrillService, Depends(get_drill_service)],
) -> DrillAnswerResponse:
    """Check if a drill answer is correct."""
    result = await service.check_answer(
        user_id=DEFAULT_USER_ID,
        word_id=request.word_id,
        user_answer=request.user_answer,
        exercise_type=request.exercise_type,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return DrillAnswerResponse(**result)
