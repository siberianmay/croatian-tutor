"""CRUD operations for User model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.app_settings import AppSettings
from app.models.user import User
from app.schemas.auth import UserRegister
from app.schemas.user import UserUpdate


class UserCRUD:
    """CRUD operations for user management."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get(self, user_id: int) -> User | None:
        """Get a user by ID."""
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user_in: UserRegister) -> User:
        """
        Create a new user with hashed password.

        Also creates default AppSettings for the user.
        """
        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            name=user_in.name,
        )
        self._db.add(user)
        await self._db.flush()
        await self._db.refresh(user)

        # Create default settings for the new user
        settings = AppSettings(user_id=user.id)
        self._db.add(settings)
        await self._db.flush()

        return user

    async def get_or_create(self, user_id: int) -> User:
        """Get existing user by ID. Raises if not found (use for authenticated users)."""
        user = await self.get(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
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
