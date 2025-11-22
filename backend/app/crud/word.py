"""CRUD operations for Word model with SM-2 SRS algorithm."""

from datetime import datetime, timedelta, timezone
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.word import Word
from app.models.enums import CEFRLevel, PartOfSpeech
from app.schemas.word import WordCreate, WordUpdate


class WordCRUD:
    """CRUD operations for vocabulary words with SRS scheduling."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, user_id: int, word_in: WordCreate) -> Word:
        """Create a new word for a user."""
        word = Word(
            user_id=user_id,
            croatian=word_in.croatian,
            english=word_in.english,
            part_of_speech=word_in.part_of_speech,
            gender=word_in.gender,
            cefr_level=word_in.cefr_level,
            next_review_at=datetime.now(timezone.utc),
        )
        self._db.add(word)
        await self._db.flush()
        await self._db.refresh(word)
        return word

    async def get(self, word_id: int, user_id: int) -> Word | None:
        """Get a word by ID for a specific user."""
        result = await self._db.execute(
            select(Word).where(Word.id == word_id, Word.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        part_of_speech: PartOfSpeech | None = None,
        cefr_level: CEFRLevel | None = None,
        search: str | None = None,
    ) -> Sequence[Word]:
        """Get multiple words with pagination and filters."""
        query = select(Word).where(Word.user_id == user_id)

        if part_of_speech:
            query = query.where(Word.part_of_speech == part_of_speech)
        if cefr_level:
            query = query.where(Word.cefr_level == cefr_level)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Word.croatian.ilike(search_pattern))
                | (Word.english.ilike(search_pattern))
            )

        query = query.order_by(Word.created_at.desc()).offset(skip).limit(limit)
        result = await self._db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        user_id: int,
        *,
        part_of_speech: PartOfSpeech | None = None,
        cefr_level: CEFRLevel | None = None,
        search: str | None = None,
    ) -> int:
        """Count words matching filters."""
        query = select(func.count(Word.id)).where(Word.user_id == user_id)

        if part_of_speech:
            query = query.where(Word.part_of_speech == part_of_speech)
        if cefr_level:
            query = query.where(Word.cefr_level == cefr_level)
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                (Word.croatian.ilike(search_pattern))
                | (Word.english.ilike(search_pattern))
            )

        result = await self._db.execute(query)
        return result.scalar_one()

    async def update(
        self, word_id: int, user_id: int, word_in: WordUpdate
    ) -> Word | None:
        """Update a word."""
        word = await self.get(word_id, user_id)
        if not word:
            return None

        update_data = word_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(word, field, value)

        await self._db.flush()
        await self._db.refresh(word)
        return word

    async def delete(self, word_id: int, user_id: int) -> bool:
        """Delete a word. Returns True if deleted, False if not found."""
        word = await self.get(word_id, user_id)
        if not word:
            return False

        await self._db.delete(word)
        await self._db.flush()
        return True

    async def get_due_words(
        self, user_id: int, *, limit: int = 20
    ) -> Sequence[Word]:
        """Get words due for review, ordered by priority."""
        now = datetime.now(timezone.utc)
        query = (
            select(Word)
            .where(Word.user_id == user_id)
            .where((Word.next_review_at <= now) | (Word.next_review_at.is_(None)))
            .order_by(
                Word.next_review_at.asc().nullsfirst(),
                Word.mastery_score.asc(),
            )
            .limit(limit)
        )
        result = await self._db.execute(query)
        return result.scalars().all()

    async def count_due_words(self, user_id: int) -> int:
        """Count words due for review."""
        now = datetime.now(timezone.utc)
        query = (
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where((Word.next_review_at <= now) | (Word.next_review_at.is_(None)))
        )
        result = await self._db.execute(query)
        return result.scalar_one()

    async def exists_for_user(self, user_id: int, croatian: str) -> bool:
        """Check if a word already exists for a user."""
        query = select(func.count(Word.id)).where(
            Word.user_id == user_id,
            func.lower(Word.croatian) == croatian.lower(),
        )
        result = await self._db.execute(query)
        return result.scalar_one() > 0

    async def process_review(
        self, word_id: int, user_id: int, *, correct: bool
    ) -> Word | None:
        """
        Process a drill review result using SM-2 algorithm.

        SM-2 Algorithm:
        - Quality rating: 0-5 (we map correct=True to 4, correct=False to 1)
        - EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        - EF minimum = 1.3
        - Interval: rep 1 = 1 day, rep 2 = 6 days, rep n = interval(n-1) * EF
        """
        word = await self.get(word_id, user_id)
        if not word:
            return None

        now = datetime.now(timezone.utc)
        word.last_reviewed_at = now

        if correct:
            word.correct_count += 1
            quality = 4  # Good response
        else:
            word.wrong_count += 1
            quality = 1  # Failed response

        # Update ease factor using SM-2 formula
        new_ef = word.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        word.ease_factor = max(1.3, new_ef)

        # Calculate mastery score (0-10) based on success rate
        total_reviews = word.correct_count + word.wrong_count
        if total_reviews > 0:
            success_rate = word.correct_count / total_reviews
            word.mastery_score = min(10, int(success_rate * 10))

        # Calculate next review interval
        if correct:
            interval_days = self._calculate_interval(
                correct_streak=word.correct_count,
                ease_factor=word.ease_factor,
            )
        else:
            # Reset to shorter interval on wrong answer
            interval_days = 1

        word.next_review_at = now + timedelta(days=interval_days)

        await self._db.flush()
        await self._db.refresh(word)
        return word

    def _calculate_interval(self, correct_streak: int, ease_factor: float) -> float:
        """
        Calculate review interval in days using SM-2.

        Intervals:
        - 1st correct: 1 day
        - 2nd correct: 6 days
        - nth correct: previous_interval * ease_factor
        """
        if correct_streak <= 1:
            return 1
        elif correct_streak == 2:
            return 6
        else:
            # For simplicity, we approximate based on streak
            # In a full implementation, you'd track actual intervals
            base_interval = 6
            for _ in range(correct_streak - 2):
                base_interval = base_interval * ease_factor
            return min(base_interval, 365)  # Cap at 1 year
