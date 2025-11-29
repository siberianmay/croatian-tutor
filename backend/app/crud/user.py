"""CRUD operations for User model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserUpdate


class UserCRUD:
    """CRUD operations for user management."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get(self, user_id: int) -> User | None:
        """Get a user by ID."""
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: int = 1) -> User:
        """Get existing user or create default user."""
        user = await self.get(user_id)
        if not user:
            user = User(id=user_id)
            self._db.add(user)
            await self._db.flush()
            await self._db.refresh(user)
        return user

    async def get_language(self, user_id: int) -> str:
        """Get user's selected language code."""
        user = await self.get_or_create(user_id)
        return user.language

    async def set_language(self, user_id: int, language_code: str) -> User:
        """Set user's selected language."""
        user = await self.get_or_create(user_id)
        user.language = language_code
        await self._db.flush()
        await self._db.refresh(user)
        return user

    async def update(self, user_id: int, user_in: UserUpdate) -> User | None:
        """Update user settings."""
        user = await self.get(user_id)
        if not user:
            return None

        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self._db.flush()
        await self._db.refresh(user)
        return user
