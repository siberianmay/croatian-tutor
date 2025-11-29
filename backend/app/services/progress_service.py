"""Progress service for dashboard statistics and context summaries."""

from datetime import date, timedelta
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.word import Word
from app.models.exercise_log import ExerciseLog
from app.models.error_log import ErrorLog
from app.models.topic_progress import TopicProgress
from app.models.grammar_topic import GrammarTopic
from app.models.enums import CEFRLevel, ErrorCategory, ExerciseType


class ProgressService:
    """Service for aggregating learning progress and generating context summaries."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_summary(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Get overall learning summary.

        Returns:
            {
                "total_words": int,
                "mastered_words": int,
                "words_due_today": int,
                "total_exercises": int,
                "total_errors": int,
                "streak_days": int,
                "current_level": str
            }
        """
        now = date.today()

        # Word counts
        total_words = await self._count_words(user_id, language)
        mastered_words = await self._count_mastered_words(user_id, language)
        due_words = await self._count_due_words(user_id, language)

        # Exercise totals
        total_exercises = await self._count_total_exercises(user_id, language)
        total_errors = await self._count_total_errors(user_id, language)

        # Streak calculation
        streak_days = await self._calculate_streak(user_id, language)

        # Determine current level based on progress
        current_level = await self._determine_level(user_id, language)

        return {
            "total_words": total_words,
            "mastered_words": mastered_words,
            "words_due_today": due_words,
            "total_exercises": total_exercises,
            "total_errors": total_errors,
            "streak_days": streak_days,
            "current_level": current_level,
        }

    async def get_vocabulary_stats(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Get vocabulary breakdown by level and mastery.

        Returns:
            {
                "by_level": {"A1": 10, "A2": 5, ...},
                "by_mastery": {"new": 5, "learning": 8, "mastered": 2},
                "recent_words": [{"croatian": str, "english": str, "mastery_score": int}]
            }
        """
        # Count by CEFR level
        by_level = {}
        for level in CEFRLevel:
            result = await self._db.execute(
                select(func.count(Word.id))
                .where(Word.user_id == user_id)
                .where(Word.language == language)
                .where(Word.cefr_level == level)
            )
            count = result.scalar_one()
            if count > 0:
                by_level[level.value] = count

        # Count by mastery category
        # new: mastery_score = 0, learning: 1-6, mastered: 7-10
        new_count = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score == 0)
        )
        learning_count = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score > 0)
            .where(Word.mastery_score < 7)
        )
        mastered_count = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score >= 7)
        )

        by_mastery = {
            "new": new_count.scalar_one(),
            "learning": learning_count.scalar_one(),
            "mastered": mastered_count.scalar_one(),
        }

        # Recent words (last 10 added)
        recent_result = await self._db.execute(
            select(Word)
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .order_by(desc(Word.created_at))
            .limit(10)
        )
        recent_words = [
            {
                "croatian": w.croatian,
                "english": w.english,
                "mastery_score": w.mastery_score,
            }
            for w in recent_result.scalars().all()
        ]

        return {
            "by_level": by_level,
            "by_mastery": by_mastery,
            "recent_words": recent_words,
        }

    async def get_topic_stats(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Get grammar topic progress overview.

        Returns:
            {
                "total_topics": int,
                "practiced_topics": int,
                "mastered_topics": int,
                "topics": [{"id": int, "name": str, "level": str, "mastery": int, "attempts": int}]
            }
        """
        # Count all topics for this language
        total_result = await self._db.execute(
            select(func.count(GrammarTopic.id))
            .where(GrammarTopic.language == language)
        )
        total_topics = total_result.scalar_one()

        # Get all topics with progress for this language
        topics_result = await self._db.execute(
            select(GrammarTopic, TopicProgress)
            .outerjoin(
                TopicProgress,
                (TopicProgress.topic_id == GrammarTopic.id)
                & (TopicProgress.user_id == user_id),
            )
            .where(GrammarTopic.language == language)
            .order_by(GrammarTopic.cefr_level, GrammarTopic.name)
        )

        topics = []
        practiced_count = 0
        mastered_count = 0

        for topic, progress in topics_result.all():
            mastery = progress.mastery_score if progress else 0
            attempts = progress.times_practiced if progress else 0

            if attempts > 0:
                practiced_count += 1
            if mastery >= 7:
                mastered_count += 1

            topics.append({
                "id": topic.id,
                "name": topic.name,
                "level": topic.cefr_level.value,
                "mastery": mastery,
                "attempts": attempts,
            })

        return {
            "total_topics": total_topics,
            "practiced_topics": practiced_count,
            "mastered_topics": mastered_count,
            "topics": topics,
        }

    async def get_activity(self, user_id: int, language: str = "hr", days: int = 14) -> dict[str, Any]:
        """
        Get recent activity timeline.

        Returns:
            {
                "daily_activity": [{"date": str, "exercises": int, "duration_minutes": int}],
                "exercise_breakdown": {"conversation": 5, "grammar": 3, ...}
            }
        """
        start_date = date.today() - timedelta(days=days - 1)

        # Daily aggregates
        daily_result = await self._db.execute(
            select(
                ExerciseLog.date,
                func.sum(ExerciseLog.exercises_completed).label("exercises"),
                func.sum(ExerciseLog.duration_minutes).label("duration"),
            )
            .where(ExerciseLog.user_id == user_id)
            .where(ExerciseLog.language == language)
            .where(ExerciseLog.date >= start_date)
            .group_by(ExerciseLog.date)
            .order_by(ExerciseLog.date)
        )

        daily_activity = [
            {
                "date": str(row.date),
                "exercises": row.exercises or 0,
                "duration_minutes": row.duration or 0,
            }
            for row in daily_result.all()
        ]

        # Exercise type breakdown (all time for this language)
        type_result = await self._db.execute(
            select(
                ExerciseLog.exercise_type,
                func.sum(ExerciseLog.exercises_completed).label("count"),
            )
            .where(ExerciseLog.user_id == user_id)
            .where(ExerciseLog.language == language)
            .group_by(ExerciseLog.exercise_type)
        )

        exercise_breakdown = {
            row.exercise_type.value: row.count or 0 for row in type_result.all()
        }

        return {
            "daily_activity": daily_activity,
            "exercise_breakdown": exercise_breakdown,
        }

    async def get_error_patterns(self, user_id: int, language: str = "hr") -> dict[str, Any]:
        """
        Get error patterns for targeted practice.

        Returns:
            {
                "by_category": {"case_error": 10, "gender_agreement": 5, ...},
                "recent_errors": [{"category": str, "details": str, "correction": str, "date": str}],
                "weak_areas": [{"category": str, "count": int, "suggestion": str}]
            }
        """
        # Error counts by category
        category_result = await self._db.execute(
            select(
                ErrorLog.error_category,
                func.count(ErrorLog.id).label("count"),
            )
            .where(ErrorLog.user_id == user_id)
            .where(ErrorLog.language == language)
            .group_by(ErrorLog.error_category)
            .order_by(desc("count"))
        )

        by_category = {
            row.error_category.value: row.count for row in category_result.all()
        }

        # Recent errors (last 10)
        recent_result = await self._db.execute(
            select(ErrorLog)
            .where(ErrorLog.user_id == user_id)
            .where(ErrorLog.language == language)
            .order_by(desc(ErrorLog.date), desc(ErrorLog.id))
            .limit(10)
        )

        recent_errors = [
            {
                "category": err.error_category.value,
                "details": err.details,
                "correction": err.correction,
                "date": str(err.date),
            }
            for err in recent_result.scalars().all()
        ]

        # Generate weak areas with suggestions
        weak_areas = []
        suggestions = {
            ErrorCategory.CASE_ERROR: "Practice noun cases with dedicated grammar exercises",
            ErrorCategory.GENDER_AGREEMENT: "Review gender agreement rules for adjectives",
            ErrorCategory.VERB_CONJUGATION: "Focus on verb conjugation patterns",
            ErrorCategory.WORD_ORDER: "Practice sentence construction exercises",
            ErrorCategory.SPELLING: "Review Croatian spelling rules and diacritics",
            ErrorCategory.VOCABULARY: "Expand vocabulary through regular drills",
            ErrorCategory.ACCENT: "Practice pronunciation with dialogue exercises",
            ErrorCategory.OTHER: "Continue general practice across all areas",
        }

        # Top 3 error categories as weak areas
        for category, count in list(by_category.items())[:3]:
            try:
                cat_enum = ErrorCategory(category)
                weak_areas.append({
                    "category": category,
                    "count": count,
                    "suggestion": suggestions.get(cat_enum, "Keep practicing!"),
                })
            except ValueError:
                continue

        return {
            "by_category": by_category,
            "recent_errors": recent_errors,
            "weak_areas": weak_areas,
        }

    async def generate_context_summary(self, user_id: int, language: str = "hr") -> str:
        """
        Generate a text summary for Gemini context.

        This provides the AI tutor with user context for personalized responses.
        """
        summary = await self.get_summary(user_id, language)
        vocab_stats = await self.get_vocabulary_stats(user_id, language)
        error_stats = await self.get_error_patterns(user_id, language)

        parts = [
            f"Student Level: {summary['current_level']}",
            f"Vocabulary: {summary['total_words']} words ({summary['mastered_words']} mastered)",
            f"Total exercises completed: {summary['total_exercises']}",
            f"Study streak: {summary['streak_days']} days",
        ]

        # Add weak areas
        if error_stats["weak_areas"]:
            weak = ", ".join(w["category"] for w in error_stats["weak_areas"])
            parts.append(f"Areas needing work: {weak}")

        # Add level distribution
        if vocab_stats["by_level"]:
            levels = ", ".join(f"{k}: {v}" for k, v in vocab_stats["by_level"].items())
            parts.append(f"Words by level: {levels}")

        return "\n".join(parts)

    async def build_gemini_context(self, user_id: int, language: str = "hr") -> str:
        """
        Build a comprehensive context block for Gemini prompts.

        This generates a structured context that follows the prompt template
        from the design docs, providing the AI with full learner context.
        """
        summary = await self.get_summary(user_id, language)
        vocab_stats = await self.get_vocabulary_stats(user_id, language)
        topic_stats = await self.get_topic_stats(user_id, language)
        activity = await self.get_activity(user_id, language, days=7)
        error_stats = await self.get_error_patterns(user_id, language)

        # Build vocabulary summary
        vocab_section = f"""[VOCABULARY SUMMARY]
{summary['total_words']} words total. Strong (7-10): {vocab_stats['by_mastery']['mastered']}, Medium (1-6): {vocab_stats['by_mastery']['learning']}, New (0): {vocab_stats['by_mastery']['new']}.
By level: {', '.join(f"{k}: {v}" for k, v in vocab_stats['by_level'].items()) if vocab_stats['by_level'] else 'None yet'}.
Due for review: {summary['words_due_today']} words."""

        # Build topic progress summary
        completed_topics = [t for t in topic_stats['topics'] if t['mastery'] >= 7]
        in_progress_topics = [t for t in topic_stats['topics'] if 0 < t['mastery'] < 7]
        not_started_topics = [t for t in topic_stats['topics'] if t['mastery'] == 0 and t['attempts'] == 0]

        completed_str = ", ".join(f"{t['name']} ({t['mastery']}/10)" for t in completed_topics[:5]) if completed_topics else "None yet"
        in_progress_str = ", ".join(f"{t['name']} ({t['mastery']}/10)" for t in in_progress_topics[:3]) if in_progress_topics else "None"
        not_started_str = ", ".join(t['name'] for t in not_started_topics[:3]) if not_started_topics else "None"

        topic_section = f"""[TOPIC PROGRESS]
Completed: {completed_str}.
In progress: {in_progress_str}.
Not started: {not_started_str}."""

        # Build activity summary
        exercise_breakdown = activity.get('exercise_breakdown', {})
        activity_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in exercise_breakdown.items() if v > 0]
        activity_str = ", ".join(activity_parts) if activity_parts else "No recent activity"

        activity_section = f"""[RECENT ACTIVITY]
Last 7 days: {activity_str}.
Study streak: {summary['streak_days']} days."""

        # Build error patterns summary
        error_section_parts = []
        if error_stats['weak_areas']:
            for area in error_stats['weak_areas'][:2]:
                error_section_parts.append(f"{area['category'].replace('_', ' ').title()}: {area['count']}x")

        error_section = f"""[ERROR PATTERNS]
{chr(10).join(error_section_parts) if error_section_parts else 'No significant error patterns yet.'}"""

        # Combine all sections
        context = f"""Here is the student's learning context:

{vocab_section}

{topic_section}

{activity_section}

{error_section}

Student's current CEFR level: {summary['current_level']}"""

        return context

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    async def _count_words(self, user_id: int, language: str) -> int:
        result = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
        )
        return result.scalar_one()

    async def _count_mastered_words(self, user_id: int, language: str) -> int:
        result = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where(Word.mastery_score >= 7)
        )
        return result.scalar_one()

    async def _count_due_words(self, user_id: int, language: str) -> int:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(func.count(Word.id))
            .where(Word.user_id == user_id)
            .where(Word.language == language)
            .where((Word.next_review_at <= now) | (Word.next_review_at.is_(None)))
        )
        return result.scalar_one()

    async def _count_total_exercises(self, user_id: int, language: str) -> int:
        result = await self._db.execute(
            select(func.sum(ExerciseLog.exercises_completed))
            .where(ExerciseLog.user_id == user_id)
            .where(ExerciseLog.language == language)
        )
        return result.scalar_one() or 0

    async def _count_total_errors(self, user_id: int, language: str) -> int:
        result = await self._db.execute(
            select(func.count(ErrorLog.id))
            .where(ErrorLog.user_id == user_id)
            .where(ErrorLog.language == language)
        )
        return result.scalar_one()

    async def _calculate_streak(self, user_id: int, language: str) -> int:
        """Calculate consecutive days of activity."""
        today = date.today()

        # Get distinct activity dates, ordered descending
        result = await self._db.execute(
            select(ExerciseLog.date)
            .where(ExerciseLog.user_id == user_id)
            .where(ExerciseLog.language == language)
            .distinct()
            .order_by(desc(ExerciseLog.date))
        )
        dates = [row.date for row in result.all()]

        if not dates:
            return 0

        # Check if today or yesterday was active
        if dates[0] not in (today, today - timedelta(days=1)):
            return 0

        streak = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == timedelta(days=1):
                streak += 1
            else:
                break

        return streak

    async def _determine_level(self, user_id: int, language: str) -> str:
        """Determine user's current level based on mastered content."""
        # Count mastered words by level
        level_mastery = {}
        for level in CEFRLevel:
            result = await self._db.execute(
                select(func.count(Word.id))
                .where(Word.user_id == user_id)
                .where(Word.language == language)
                .where(Word.cefr_level == level)
                .where(Word.mastery_score >= 7)
            )
            level_mastery[level] = result.scalar_one()

        # Determine level: need at least 10 mastered words at a level to "complete" it
        current = CEFRLevel.A1
        for level in [CEFRLevel.A1, CEFRLevel.A2, CEFRLevel.B1, CEFRLevel.B2, CEFRLevel.C1]:
            if level_mastery.get(level, 0) >= 10:
                # Move to next level
                next_levels = {
                    CEFRLevel.A1: CEFRLevel.A2,
                    CEFRLevel.A2: CEFRLevel.B1,
                    CEFRLevel.B1: CEFRLevel.B2,
                    CEFRLevel.B2: CEFRLevel.C1,
                    CEFRLevel.C1: CEFRLevel.C2,
                }
                current = next_levels.get(level, level)

        return current.value
