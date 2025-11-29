"""CRUD operations for AppSettings model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings
from app.schemas.app_settings import AppSettingsUpdate


class AppSettingsCRUD:
    """
    CRUD operations for per-user application settings.

    Each user has their own settings record.
    """

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get(self, user_id: int) -> AppSettings:
        """
        Get settings for a specific user.

        Raises ValueError if settings don't exist (should be created on registration).
        """
        result = await self._db.execute(
            select(AppSettings).where(AppSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()

        if settings is None:
            raise ValueError(f"Settings not found for user {user_id}")

        return settings

    async def get_or_create(self, user_id: int) -> AppSettings:
        """
        Get settings for user, creating defaults if not found.

        Use this for backward compatibility during migration.
        """
        result = await self._db.execute(
            select(AppSettings).where(AppSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()

        if settings is None:
            settings = AppSettings(user_id=user_id)
            self._db.add(settings)
            await self._db.flush()
            await self._db.refresh(settings)

        return settings

    async def create(self, user_id: int) -> AppSettings:
        """
        Create default settings for a user.

        Called during user registration.
        """
        settings = AppSettings(user_id=user_id)
        self._db.add(settings)
        await self._db.flush()
        await self._db.refresh(settings)
        return settings

    async def update(self, user_id: int, settings_in: AppSettingsUpdate) -> AppSettings:
        """
        Update settings for a specific user.

        Only updates fields that are not None in the input.
        """
        settings = await self.get(user_id)

        # Update only provided fields
        update_data = settings_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(settings, field, value)

        await self._db.flush()
        await self._db.refresh(settings)
        return settings
