"""Shared API dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import UserCRUD
from app.database import get_db

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_user_crud(db: Annotated[AsyncSession, Depends(get_db)]) -> UserCRUD:
    """Dependency for UserCRUD."""
    return UserCRUD(db)


async def get_current_language(
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
) -> str:
    """
    Get the current user's selected language code.

    Returns the language code (e.g., 'hr' for Croatian, 'it' for Italian).
    """
    return await user_crud.get_language(DEFAULT_USER_ID)
