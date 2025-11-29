"""CRUD operations for Language model."""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language import Language
from app.schemas.language import LanguageCreate


class LanguageCRUD:
    """CRUD operations for supported languages."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, language_in: LanguageCreate) -> Language:
        """Create a new language."""
        language = Language(
            code=language_in.code,
            name=language_in.name,
            native_name=language_in.native_name,
            is_active=language_in.is_active,
        )
        self._db.add(language)
        await self._db.flush()
        await self._db.refresh(language)
        return language

    async def get(self, code: str) -> Language | None:
        """Get a language by code."""
        result = await self._db.execute(
            select(Language).where(Language.code == code)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> Sequence[Language]:
        """Get multiple languages with pagination."""
        query = select(Language)

        if active_only:
            query = query.where(Language.is_active == True)

        query = query.order_by(Language.name).offset(skip).limit(limit)

        result = await self._db.execute(query)
        return result.scalars().all()

    async def get_all_active(self) -> Sequence[Language]:
        """Get all active languages."""
        result = await self._db.execute(
            select(Language)
            .where(Language.is_active == True)
            .order_by(Language.name)
        )
        return result.scalars().all()

    async def exists(self, code: str) -> bool:
        """Check if a language code exists."""
        result = await self._db.execute(
            select(Language.code).where(Language.code == code)
        )
        return result.scalar_one_or_none() is not None

    async def set_active(self, code: str, is_active: bool) -> Language | None:
        """Activate or deactivate a language."""
        language = await self.get(code)
        if language:
            language.is_active = is_active
            await self._db.flush()
            await self._db.refresh(language)
        return language
