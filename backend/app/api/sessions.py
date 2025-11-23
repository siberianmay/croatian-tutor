"""Session API endpoints for tracking learning sessions."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.crud.session import SessionCRUD
from app.models.enums import ExerciseType
from app.schemas.session import (
    SessionCreate,
    SessionEnd,
    SessionResponse,
    SessionListResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_session_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> SessionCRUD:
    """Dependency for SessionCRUD."""
    return SessionCRUD(db)


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    request: SessionCreate,
    crud: Annotated[SessionCRUD, Depends(get_session_crud)],
) -> SessionResponse:
    """
    Start a new learning session.

    Creates a session record with the current timestamp as start time.
    """
    session = await crud.create(DEFAULT_USER_ID, request)
    return SessionResponse.model_validate(session)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    crud: Annotated[SessionCRUD, Depends(get_session_crud)],
    skip: int = 0,
    limit: int = 50,
    exercise_type: ExerciseType | None = None,
) -> SessionListResponse:
    """
    List learning sessions.

    Supports pagination and filtering by exercise type.
    """
    sessions = await crud.get_multi(
        DEFAULT_USER_ID,
        skip=skip,
        limit=limit,
        exercise_type=exercise_type,
    )
    total = await crud.count(DEFAULT_USER_ID, exercise_type=exercise_type)

    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.get("/active", response_model=SessionResponse | None)
async def get_active_session(
    crud: Annotated[SessionCRUD, Depends(get_session_crud)],
    exercise_type: ExerciseType | None = None,
) -> SessionResponse | None:
    """
    Get the currently active (not ended) session.

    Returns None if no active session exists.
    """
    session = await crud.get_active(DEFAULT_USER_ID, exercise_type)
    if session:
        return SessionResponse.model_validate(session)
    return None


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    crud: Annotated[SessionCRUD, Depends(get_session_crud)],
) -> SessionResponse:
    """Get a specific session by ID."""
    session = await crud.get(session_id, DEFAULT_USER_ID)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return SessionResponse.model_validate(session)


@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: int,
    request: SessionEnd,
    crud: Annotated[SessionCRUD, Depends(get_session_crud)],
) -> SessionResponse:
    """
    End a learning session.

    Calculates duration and stores the outcome. Returns error if session
    is already ended or not found.
    """
    session = await crud.end_session(session_id, DEFAULT_USER_ID, request)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session not found or already ended",
        )
    return SessionResponse.model_validate(session)
