"""
Analytics Repository — Data access for mastery, weak topics, and recommendations.
"""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db.analytics import UserTopicMastery, WeakTopic, LearningRecommendation


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Topic Mastery ---
    async def upsert_topic_mastery(
        self, user_id: str, topic: str, subtopic: str = "",
        total_attempts: int = 0, correct_attempts: int = 0,
        accuracy: float = 0.0, avg_response_time: float = 0.0,
        current_difficulty: str = "Medium", skill_score: float = 50.0,
        mastery_level: str = "NOVICE"
    ) -> UserTopicMastery:
        """Create or update topic mastery for a user."""
        result = await self.db.execute(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user_id,
                UserTopicMastery.topic == topic,
                UserTopicMastery.subtopic == subtopic,
            )
        )
        mastery = result.scalar_one_or_none()

        if mastery:
            mastery.total_attempts = total_attempts
            mastery.correct_attempts = correct_attempts
            mastery.accuracy = accuracy
            mastery.avg_response_time = avg_response_time
            mastery.current_difficulty = current_difficulty
            mastery.skill_score = skill_score
            mastery.mastery_level = mastery_level
            mastery.last_attempted = datetime.now(timezone.utc)
        else:
            mastery = UserTopicMastery(
                user_id=user_id, topic=topic, subtopic=subtopic,
                total_attempts=total_attempts, correct_attempts=correct_attempts,
                accuracy=accuracy, avg_response_time=avg_response_time,
                current_difficulty=current_difficulty, skill_score=skill_score,
                mastery_level=mastery_level,
            )
            self.db.add(mastery)

        await self.db.flush()
        return mastery

    async def get_user_mastery(self, user_id: str) -> List[UserTopicMastery]:
        result = await self.db.execute(
            select(UserTopicMastery)
            .where(UserTopicMastery.user_id == user_id)
            .order_by(UserTopicMastery.skill_score.desc())
        )
        return list(result.scalars().all())

    async def get_topic_mastery(self, user_id: str, topic: str) -> Optional[UserTopicMastery]:
        result = await self.db.execute(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user_id,
                UserTopicMastery.topic == topic,
            )
        )
        return result.scalar_one_or_none()

    # --- Weak Topics ---
    async def replace_weak_topics(self, user_id: str, weak_topics: List[dict]) -> List[WeakTopic]:
        """Clear and re-insert weak topics for a user (recalculated after each quiz)."""
        await self.db.execute(
            delete(WeakTopic).where(WeakTopic.user_id == user_id)
        )
        new_topics = []
        for wt in weak_topics:
            topic = WeakTopic(user_id=user_id, **wt)
            self.db.add(topic)
            new_topics.append(topic)
        await self.db.flush()
        return new_topics

    async def get_weak_topics(self, user_id: str, limit: int = 10) -> List[WeakTopic]:
        result = await self.db.execute(
            select(WeakTopic)
            .where(WeakTopic.user_id == user_id)
            .order_by(WeakTopic.weakness_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # --- Recommendations ---
    async def create_recommendation(self, **kwargs) -> LearningRecommendation:
        rec = LearningRecommendation(**kwargs)
        self.db.add(rec)
        await self.db.flush()
        return rec

    async def get_recommendations(self, user_id: str, limit: int = 20) -> List[LearningRecommendation]:
        result = await self.db.execute(
            select(LearningRecommendation)
            .where(LearningRecommendation.user_id == user_id)
            .order_by(LearningRecommendation.priority, LearningRecommendation.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_recommendation_completed(self, rec_id: str) -> bool:
        result = await self.db.execute(
            select(LearningRecommendation).where(LearningRecommendation.id == rec_id)
        )
        rec = result.scalar_one_or_none()
        if rec:
            rec.is_completed = True
            await self.db.flush()
            return True
        return False
