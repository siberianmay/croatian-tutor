"""Drill service for vocabulary practice sessions."""

import random
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.word import WordCRUD
from app.database import get_db
from app.models.word import Word
from app.models.enums import ExerciseType


class DrillService:
    """Service for managing vocabulary drill sessions."""

    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self._db = db
        self._word_crud = WordCRUD(db)

    async def get_drill_words(
        self,
        user_id: int,
        exercise_type: ExerciseType,
        count: int = 10,
    ) -> list[Word]:
        """
        Get words for a drill session.

        Prioritizes:
        1. Words due for review (SRS)
        2. Low mastery words
        3. Random selection if needed
        """
        # Get due words first
        due_words = await self._word_crud.get_due_words(user_id, limit=count)
        words = list(due_words)

        # If we need more words, get low mastery ones
        if len(words) < count:
            remaining = count - len(words)
            all_words = await self._word_crud.get_multi(
                user_id,
                skip=0,
                limit=100,
            )
            # Filter out words already selected and sort by mastery
            existing_ids = {w.id for w in words}
            candidates = [w for w in all_words if w.id not in existing_ids]
            candidates.sort(key=lambda w: (w.mastery_score, random.random()))
            words.extend(candidates[:remaining])

        # Shuffle for variety
        random.shuffle(words)
        return words[:count]

    async def get_cr_to_en_drill(
        self,
        user_id: int,
        count: int = 10,
    ) -> list[dict]:
        """
        Get Croatian to English drill items.

        Returns list of {word_id, croatian, expected_answer}
        """
        words = await self.get_drill_words(
            user_id, ExerciseType.VOCABULARY_CR_EN, count
        )
        return [
            {
                "word_id": w.id,
                "prompt": w.croatian,
                "expected_answer": w.english,
                "part_of_speech": w.part_of_speech.value,
                "gender": w.gender.value if w.gender else None,
            }
            for w in words
        ]

    async def get_en_to_cr_drill(
        self,
        user_id: int,
        count: int = 10,
    ) -> list[dict]:
        """
        Get English to Croatian drill items.

        Returns list of {word_id, english, expected_answer}
        """
        words = await self.get_drill_words(
            user_id, ExerciseType.VOCABULARY_EN_CR, count
        )
        return [
            {
                "word_id": w.id,
                "prompt": w.english,
                "expected_answer": w.croatian,
                "part_of_speech": w.part_of_speech.value,
                "cefr_level": w.cefr_level.value,
            }
            for w in words
        ]

    async def check_answer(
        self,
        user_id: int,
        word_id: int,
        user_answer: str,
        exercise_type: ExerciseType,
    ) -> dict:
        """
        Check if user's answer is correct.

        Returns {correct, expected_answer, word}
        """
        word = await self._word_crud.get(word_id, user_id)
        if not word:
            return {"error": "Word not found"}

        # Determine expected answer based on exercise type
        if exercise_type == ExerciseType.VOCABULARY_CR_EN:
            expected = word.english
        elif exercise_type == ExerciseType.VOCABULARY_EN_CR:
            expected = word.croatian
        else:
            return {"error": "Invalid exercise type for vocabulary drill"}

        # Case-insensitive comparison, strip whitespace
        correct = user_answer.strip().lower() == expected.strip().lower()

        return {
            "correct": correct,
            "expected_answer": expected,
            "user_answer": user_answer,
            "word_id": word_id,
        }
