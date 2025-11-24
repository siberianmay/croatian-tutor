"""CRUD operations for AppSettings model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings
from app.schemas.app_settings import AppSettingsUpdate


class AppSettingsCRUD:
    """
    CRUD operations for application settings.

    Uses singleton pattern - always operates on row with id=1.
    Auto-creates default row if missing.
    """

    SINGLETON_ID = 1

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get(self) -> AppSettings:
        """
        Get application settings.

        Auto-creates default settings if row doesn't exist.
        """
        result = await self._db.execute(
            select(AppSettings).where(AppSettings.id == self.SINGLETON_ID)
        )
        settings = result.scalar_one_or_none()

        if settings is None:
            # Create default settings
            settings = AppSettings(id=self.SINGLETON_ID)
            self._db.add(settings)
            await self._db.flush()
            await self._db.refresh(settings)

        return settings

    async def update(self, settings_in: AppSettingsUpdate) -> AppSettings:
        """
        Update application settings.

        Only updates fields that are not None in the input.
        """
        settings = await self.get()

        # Update only provided fields
        update_data = settings_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(settings, field, value)

        await self._db.flush()
        await self._db.refresh(settings)
        return settings
