"""Analytics service for advanced SRS metrics and learning insights."""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.word import Word
from app.models.enums import CEFRLevel, PartOfSpeech


class AnalyticsService:
    """Service for advanced learning analytics and SRS insights."""

    # Leech threshold: if wrong_count >= this AND failure_rate >= threshold, it's a leech
    LEECH_MIN_ATTEMPTS = 4
    LEECH_FAILURE_RATE = 0.5  # 50% failure rate

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_leeches(self, user_id: int, language: str = "hr", limit: int = 20) -> dict[str, Any]:
        """
        Detect leech words - words with high failure rates that waste review time.

        A leech is a word with:
        - At least LEECH_MIN_ATTEMPTS total attempts
        - Failure rate >= LEECH_FAILURE_RATE

        Returns:
            {
                "leeches": [
                    {
                        "id": int,
                        "croatian": str,
                        "english": str,
                        "correct_count": int,
                        "wrong_count": int,
                        "failure_rate": float,
                        "cefr_level": str,
                        "part_of_speech": str
                    }
                ],
                "total_leeches": int,
                "threshold": {"min_attempts": int, "failure_rate": float}
            }
        """
        # Calculate total attempts and failure rate
        total_attempts = Word.correct_count + Word.wrong_count
        failure_rate = case(
            (total_attempts > 0, Word.wrong_count * 1.0 / total_attempts),
            else_=0.0
        )

        result = await self._db.execute(
            select(Word)
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(total_attempts >= self.LEECH_MIN_ATTEMPTS)
            .where(failure_rate >= self.LEECH_FAILURE_RATE)
            .order_by((Word.wrong_count * 1.0 / total_attempts).desc())
            .limit(limit)
        )

        leeches = []
        for word in result.scalars().all():
            total = word.correct_count + word.wrong_count
            rate = word.wrong_count / total if total > 0 else 0
            leeches.append({
                "id": word.id,
                "croatian": word.croatian,
                "english": word.english,
                "correct_count": word.correct_count,
                "wrong_count": word.wrong_count,
                "failure_rate": round(rate, 2),
                "cefr_level": word.cefr_level.value,
                "part_of_speech": word.part_of_speech.value,
            })

        # Count total leeches
        count_result = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(total_attempts >= self.LEECH_MIN_ATTEMPTS)
            .where(failure_rate >= self.LEECH_FAILURE_RATE)
        )
        total_leeches = count_result.scalar_one()

        return {
            "leeches": leeches,
            "total_leeches": total_leeches,
            "threshold": {
                "min_attempts": self.LEECH_MIN_ATTEMPTS,
                "failure_rate": self.LEECH_FAILURE_RATE,
            },
        }

    async def get_review_forecast(self, user_id: int, language: str = "hr", days: int = 7) -> dict[str, Any]:
        """
        Forecast upcoming reviews by day.

        Returns:
            {
                "forecast": [
                    {"date": "2025-01-15", "count": 10, "is_today": bool}
                ],
                "total_upcoming": int,
                "overdue": int
            }
        """
        now = datetime.now(timezone.utc)
        today = now.date()

        # Count overdue reviews (past due or never reviewed)
        overdue_result = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(
                (Word.next_review_at < now) | (Word.next_review_at.is_(None))
            )
        )
        overdue = overdue_result.scalar_one()

        # Forecast for upcoming days
        forecast = []
        total_upcoming = 0

        for day_offset in range(days):
            target_date = today + timedelta(days=day_offset)
            start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)

            count_result = await self._db.execute(
                select(func.count(Word.id))
                .where(Word.user_id == user_id)
                .where(Word.language == language)
                .where(Word.next_review_at >= start_of_day)
                .where(Word.next_review_at <= end_of_day)
            )
            count = count_result.scalar_one()
            total_upcoming += count

            forecast.append({
                "date": str(target_date),
                "count": count,
                "is_today": day_offset == 0,
            })

        return {
            "forecast": forecast,
            "total_upcoming": total_upcoming,
            "overdue": overdue,
        }

    async def get_learning_velocity(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Calculate learning velocity metrics.

        Returns:
            {
                "words_added_this_week": int,
                "words_added_last_week": int,
                "words_mastered_this_week": int,
                "words_mastered_total": int,
                "retention_rate": float,  # correct / (correct + wrong)
                "avg_ease_factor": float,
                "velocity_trend": "improving" | "stable" | "declining"
            }
        """
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        last_week_start = week_start - timedelta(days=7)
        now = datetime.now(timezone.utc)

        # Words added this week
        this_week_start_dt = datetime.combine(week_start, datetime.min.time()).replace(tzinfo=timezone.utc)
        last_week_start_dt = datetime.combine(last_week_start, datetime.min.time()).replace(tzinfo=timezone.utc)

        added_this_week = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.created_at >= this_week_start_dt)
        )
        words_added_this_week = added_this_week.scalar_one()

        added_last_week = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.created_at >= last_week_start_dt)
            .where(Word.created_at < this_week_start_dt)
        )
        words_added_last_week = added_last_week.scalar_one()

        # Words mastered this week (mastery_score >= 7 AND last_reviewed_at this week)
        mastered_this_week = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score >= 7)
            .where(Word.last_reviewed_at >= this_week_start_dt)
        )
        words_mastered_this_week = mastered_this_week.scalar_one()

        # Total mastered
        mastered_total = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score >= 7)
        )
        words_mastered_total = mastered_total.scalar_one()

        # Retention rate (overall correct / total attempts)
        totals = await self._db.execute(
            select(
                func.sum(Word.correct_count).label("correct"),
                func.sum(Word.wrong_count).label("wrong"),
            )
            .where(Word.user_id == user_id)
            .where(Word.language == language)
        )
        row = totals.one()
        correct = row.correct or 0
        wrong = row.wrong or 0
        retention_rate = round(correct / (correct + wrong), 2) if (correct + wrong) > 0 else 0.0

        # Average ease factor
        avg_ef = await self._db.execute(
            select(func.avg(Word.ease_factor))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.correct_count + Word.wrong_count > 0)  # Only reviewed words
        )
        avg_ease_factor = round(avg_ef.scalar_one() or 2.5, 2)

        # Velocity trend
        if words_added_this_week > words_added_last_week * 1.2:
            velocity_trend = "improving"
        elif words_added_this_week < words_added_last_week * 0.8:
            velocity_trend = "declining"
        else:
            velocity_trend = "stable"

        return {
            "words_added_this_week": words_added_this_week,
            "words_added_last_week": words_added_last_week,
            "words_mastered_this_week": words_mastered_this_week,
            "words_mastered_total": words_mastered_total,
            "retention_rate": retention_rate,
            "avg_ease_factor": avg_ease_factor,
            "velocity_trend": velocity_trend,
        }

    async def get_difficulty_breakdown(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Analyze performance by word characteristics.

        Returns:
            {
                "by_pos": {
                    "noun": {"count": 50, "avg_mastery": 6.2, "failure_rate": 0.15},
                    ...
                },
                "by_level": {
                    "A1": {"count": 100, "avg_mastery": 7.5, "failure_rate": 0.10},
                    ...
                },
                "hardest_pos": str,
                "hardest_level": str
            }
        """
        by_pos = {}
        by_level = {}

        # Stats by part of speech
        for pos in PartOfSpeech:
            result = await self._db.execute(
                select(
                    func.count(Word.id).label("count"),
                    func.avg(Word.mastery_score).label("avg_mastery"),
                    func.sum(Word.correct_count).label("correct"),
                    func.sum(Word.wrong_count).label("wrong"),
                )
                .where(Word.user_id == user_id)
                .where(Word.language == language)
                .where(Word.part_of_speech == pos)
            )
            row = result.one()
            if row.count and row.count > 0:
                correct = row.correct or 0
                wrong = row.wrong or 0
                total = correct + wrong
                by_pos[pos.value] = {
                    "count": row.count,
                    "avg_mastery": round(float(row.avg_mastery or 0), 1),
                    "failure_rate": round(wrong / total, 2) if total > 0 else 0.0,
                }

        # Stats by CEFR level
        for level in CEFRLevel:
            result = await self._db.execute(
                select(
                    func.count(Word.id).label("count"),
                    func.avg(Word.mastery_score).label("avg_mastery"),
                    func.sum(Word.correct_count).label("correct"),
                    func.sum(Word.wrong_count).label("wrong"),
                )
                .where(Word.user_id == user_id)
                .where(Word.language == language)
                .where(Word.cefr_level == level)
            )
            row = result.one()
            if row.count and row.count > 0:
                correct = row.correct or 0
                wrong = row.wrong or 0
                total = correct + wrong
                by_level[level.value] = {
                    "count": row.count,
                    "avg_mastery": round(float(row.avg_mastery or 0), 1),
                    "failure_rate": round(wrong / total, 2) if total > 0 else 0.0,
                }

        # Find hardest categories (highest failure rate with meaningful data)
        hardest_pos = None
        hardest_pos_rate = -1
        for pos, stats in by_pos.items():
            if stats["count"] >= 5 and stats["failure_rate"] > hardest_pos_rate:
                hardest_pos_rate = stats["failure_rate"]
                hardest_pos = pos

        hardest_level = None
        hardest_level_rate = -1
        for level, stats in by_level.items():
            if stats["count"] >= 5 and stats["failure_rate"] > hardest_level_rate:
                hardest_level_rate = stats["failure_rate"]
                hardest_level = level

        return {
            "by_pos": by_pos,
            "by_level": by_level,
            "hardest_pos": hardest_pos,
            "hardest_level": hardest_level,
        }

    async def get_full_analytics(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """Get all analytics in one call."""
        leeches = await self.get_leeches(user_id, language)
        forecast = await self.get_review_forecast(user_id, language)
        velocity = await self.get_learning_velocity(user_id, language)
        difficulty = await self.get_difficulty_breakdown(user_id, language)

        return {
            "leeches": leeches,
            "forecast": forecast,
            "velocity": velocity,
            "difficulty": difficulty,
        }
