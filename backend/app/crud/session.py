"""CRUD operations for Session model."""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.enums import ExerciseType
from app.schemas.session import SessionCreate, SessionEnd


class SessionCRUD:
    """CRUD operations for learning sessions."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, user_id: int, session_in: SessionCreate) -> Session:
        """Create a new session (start a learning session)."""
        session = Session(
            user_id=user_id,
            exercise_type=session_in.exercise_type,
            started_at=datetime.now(timezone.utc),
        )
        self._db.add(session)
        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def get(self, session_id: int, user_id: int) -> Session | None:
        """Get a session by ID for a specific user."""
        result = await self._db.execute(
            select(Session).where(Session.id == session_id, Session.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active(self, user_id: int, exercise_type: ExerciseType | None = None) -> Session | None:
        """Get the most recent active (not ended) session for a user."""
        query = (
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.ended_at.is_(None))
        )
        if exercise_type:
            query = query.where(Session.exercise_type == exercise_type)
        query = query.order_by(Session.started_at.desc()).limit(1)

        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
        exercise_type: ExerciseType | None = None,
    ) -> Sequence[Session]:
        """Get multiple sessions with pagination and optional filter."""
        query = (
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(Session.started_at.desc())
        )

        if exercise_type:
            query = query.where(Session.exercise_type == exercise_type)

        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        user_id: int,
        *,
        exercise_type: ExerciseType | None = None,
    ) -> int:
        """Count sessions matching filters."""
        query = select(func.count(Session.id)).where(Session.user_id == user_id)

        if exercise_type:
            query = query.where(Session.exercise_type == exercise_type)

        result = await self._db.execute(query)
        return result.scalar_one()

    async def end_session(
        self, session_id: int, user_id: int, session_end: SessionEnd
    ) -> Session | None:
        """
        End a session, calculating duration and storing outcome.

        Returns None if session not found or already ended.
        """
        session = await self.get(session_id, user_id)
        if not session or session.ended_at is not None:
            return None

        now = datetime.now(timezone.utc)
        session.ended_at = now
        session.outcome = session_end.outcome

        # Calculate duration in minutes
        duration = now - session.started_at
        session.duration_minutes = int(duration.total_seconds() / 60)

        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def get_or_create_active(
        self, user_id: int, exercise_type: ExerciseType
    ) -> tuple[Session, bool]:
        """
        Get an active session or create a new one.

        Returns:
            Tuple of (session, created) where created is True if a new session was created.
        """
        existing = await self.get_active(user_id, exercise_type)
        if existing:
            return existing, False

        session_in = SessionCreate(exercise_type=exercise_type)
        new_session = await self.create(user_id, session_in)
        return new_session, True
