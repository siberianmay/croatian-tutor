"""CRUD operations for GrammarTopic and TopicProgress models."""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grammar_topic import GrammarTopic
from app.models.topic_progress import TopicProgress
from app.models.enums import CEFRLevel
from app.schemas.grammar_topic import GrammarTopicCreate, GrammarTopicUpdate


class GrammarTopicCRUD:
    """CRUD operations for grammar topics."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, topic_in: GrammarTopicCreate) -> GrammarTopic:
        """Create a new grammar topic."""
        topic = GrammarTopic(
            name=topic_in.name,
            cefr_level=topic_in.cefr_level,
            prerequisite_ids=topic_in.prerequisite_ids,
            rule_description=topic_in.rule_description,
            display_order=topic_in.display_order,
        )
        self._db.add(topic)
        await self._db.flush()
        await self._db.refresh(topic)
        return topic

    async def get(self, topic_id: int) -> GrammarTopic | None:
        """Get a topic by ID."""
        result = await self._db.execute(
            select(GrammarTopic).where(GrammarTopic.id == topic_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> GrammarTopic | None:
        """Get a topic by name."""
        result = await self._db.execute(
            select(GrammarTopic).where(func.lower(GrammarTopic.name) == name.lower())
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        cefr_level: CEFRLevel | None = None,
    ) -> Sequence[GrammarTopic]:
        """Get multiple topics with pagination and filters."""
        query = select(GrammarTopic)

        if cefr_level:
            query = query.where(GrammarTopic.cefr_level == cefr_level)

        query = query.order_by(
            GrammarTopic.cefr_level.asc(),
            GrammarTopic.display_order.asc(),
            GrammarTopic.name.asc(),
        ).offset(skip).limit(limit)

        result = await self._db.execute(query)
        return result.scalars().all()

    async def count(self, *, cefr_level: CEFRLevel | None = None) -> int:
        """Count topics matching filters."""
        query = select(func.count(GrammarTopic.id))

        if cefr_level:
            query = query.where(GrammarTopic.cefr_level == cefr_level)

        result = await self._db.execute(query)
        return result.scalar_one()

    async def update(
        self, topic_id: int, topic_in: GrammarTopicUpdate
    ) -> GrammarTopic | None:
        """Update a topic."""
        topic = await self.get(topic_id)
        if not topic:
            return None

        update_data = topic_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(topic, field, value)

        await self._db.flush()
        await self._db.refresh(topic)
        return topic

    async def delete(self, topic_id: int) -> bool:
        """Delete a topic. Returns True if deleted, False if not found."""
        topic = await self.get(topic_id)
        if not topic:
            return False

        await self._db.delete(topic)
        await self._db.flush()
        return True

    async def set_rule_description(
        self, topic_id: int, rule_description: str
    ) -> GrammarTopic | None:
        """Set the rule description for a topic (Gemini-generated)."""
        topic = await self.get(topic_id)
        if not topic:
            return None

        topic.rule_description = rule_description
        await self._db.flush()
        await self._db.refresh(topic)
        return topic


class TopicProgressCRUD:
    """CRUD operations for user's topic progress."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_or_create(
        self, user_id: int, topic_id: int
    ) -> TopicProgress:
        """Get existing progress or create new record."""
        result = await self._db.execute(
            select(TopicProgress).where(
                TopicProgress.user_id == user_id,
                TopicProgress.topic_id == topic_id,
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = TopicProgress(
                user_id=user_id,
                topic_id=topic_id,
                mastery_score=0,
                times_practiced=0,
            )
            self._db.add(progress)
            await self._db.flush()
            await self._db.refresh(progress)

        return progress

    async def get_user_progress(
        self, user_id: int, *, cefr_level: CEFRLevel | None = None
    ) -> Sequence[TopicProgress]:
        """Get all progress records for a user."""
        query = (
            select(TopicProgress)
            .join(GrammarTopic)
            .where(TopicProgress.user_id == user_id)
        )

        if cefr_level:
            query = query.where(GrammarTopic.cefr_level == cefr_level)

        query = query.order_by(
            GrammarTopic.cefr_level.asc(),
            GrammarTopic.display_order.asc(),
        )

        result = await self._db.execute(query)
        return result.scalars().all()

    async def update_progress(
        self,
        user_id: int,
        topic_id: int,
        *,
        score_delta: int = 0,
        correct: bool | None = None,
    ) -> TopicProgress:
        """
        Update user's progress on a topic after practice.

        Args:
            user_id: User ID
            topic_id: Topic ID
            score_delta: Direct change to mastery score
            correct: If provided, adjusts score based on answer correctness
        """
        progress = await self.get_or_create(user_id, topic_id)

        progress.times_practiced += 1
        progress.last_practiced_at = datetime.now(timezone.utc)

        if correct is not None:
            # Adjust score based on correctness
            if correct:
                progress.mastery_score = min(10, progress.mastery_score + 1)
            else:
                progress.mastery_score = max(0, progress.mastery_score - 1)
        elif score_delta:
            new_score = progress.mastery_score + score_delta
            progress.mastery_score = max(0, min(10, new_score))

        await self._db.flush()
        await self._db.refresh(progress)
        return progress

    async def get_weak_topics(
        self, user_id: int, *, limit: int = 5
    ) -> Sequence[TopicProgress]:
        """Get topics with lowest mastery scores for targeted practice."""
        result = await self._db.execute(
            select(TopicProgress)
            .where(TopicProgress.user_id == user_id)
            .where(TopicProgress.times_practiced > 0)
            .order_by(TopicProgress.mastery_score.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_unpracticed_topics(
        self, user_id: int, *, limit: int = 5
    ) -> Sequence[GrammarTopic]:
        """Get topics the user hasn't practiced yet."""
        # Get topic IDs the user has practiced
        practiced_subq = (
            select(TopicProgress.topic_id)
            .where(TopicProgress.user_id == user_id)
            .scalar_subquery()
        )

        result = await self._db.execute(
            select(GrammarTopic)
            .where(GrammarTopic.id.not_in(practiced_subq))
            .order_by(GrammarTopic.cefr_level.asc(), GrammarTopic.display_order.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_learnt_topic_ids(self, user_id: int) -> set[int]:
        """Get set of topic IDs that the user has marked as learnt."""
        result = await self._db.execute(
            select(TopicProgress.topic_id).where(TopicProgress.user_id == user_id)
        )
        return set(result.scalars().all())

    async def get_learnt_topics(self, user_id: int) -> Sequence[GrammarTopic]:
        """Get all topics the user has marked as learnt."""
        result = await self._db.execute(
            select(GrammarTopic)
            .join(TopicProgress, TopicProgress.topic_id == GrammarTopic.id)
            .where(TopicProgress.user_id == user_id)
            .order_by(GrammarTopic.cefr_level.asc(), GrammarTopic.display_order.asc())
        )
        return result.scalars().all()

    async def mark_as_learnt(self, user_id: int, topic_id: int) -> TopicProgress:
        """Mark a topic as learnt by creating a TopicProgress record."""
        return await self.get_or_create(user_id, topic_id)
