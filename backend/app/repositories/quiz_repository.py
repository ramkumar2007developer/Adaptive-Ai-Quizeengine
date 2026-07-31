"""
Quiz Repository — Data access layer for Quiz, Question, and QuizAttempt entities.
"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db.quiz import Quiz, Question, QuizAttempt


class QuizRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Quiz ---
    async def create_quiz(self, **kwargs) -> Quiz:
        quiz = Quiz(**kwargs)
        self.db.add(quiz)
        await self.db.flush()
        return quiz

    async def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        result = await self.db.execute(select(Quiz).where(Quiz.id == quiz_id))
        return result.scalar_one_or_none()

    async def update_quiz(self, quiz: Quiz) -> Quiz:
        await self.db.flush()
        return quiz

    async def get_user_quizzes(self, user_id: str, limit: int = 50) -> List[Quiz]:
        result = await self.db.execute(
            select(Quiz)
            .where(Quiz.user_id == user_id)
            .order_by(Quiz.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_completed_quizzes(self, user_id: str) -> List[Quiz]:
        result = await self.db.execute(
            select(Quiz)
            .where(Quiz.user_id == user_id, Quiz.status == "COMPLETED")
            .order_by(Quiz.started_at.desc())
        )
        return list(result.scalars().all())

    # --- Question ---
    async def create_question(self, **kwargs) -> Question:
        question = Question(**kwargs)
        self.db.add(question)
        await self.db.flush()
        return question

    async def get_question(self, question_id: str) -> Optional[Question]:
        result = await self.db.execute(select(Question).where(Question.id == question_id))
        return result.scalar_one_or_none()

    async def get_quiz_questions(self, quiz_id: str) -> List[Question]:
        result = await self.db.execute(
            select(Question)
            .where(Question.quiz_id == quiz_id)
            .order_by(Question.question_number)
        )
        return list(result.scalars().all())

    # --- Attempt ---
    async def create_attempt(self, **kwargs) -> QuizAttempt:
        attempt = QuizAttempt(**kwargs)
        self.db.add(attempt)
        await self.db.flush()
        return attempt

    async def get_quiz_attempts(self, quiz_id: str) -> List[QuizAttempt]:
        result = await self.db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.quiz_id == quiz_id)
            .order_by(QuizAttempt.created_at)
        )
        return list(result.scalars().all())

    async def get_user_attempts(self, user_id: str, limit: int = 200) -> List[QuizAttempt]:
        result = await self.db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_attempts_for_topic(self, user_id: str, topic: str) -> List[QuizAttempt]:
        """Get all attempts for a specific user+topic by joining with Questions."""
        result = await self.db.execute(
            select(QuizAttempt)
            .join(Question, QuizAttempt.question_id == Question.id)
            .where(QuizAttempt.user_id == user_id, Question.topic == topic)
            .order_by(QuizAttempt.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_user_attempts(self, user_id: str) -> int:
        result = await self.db.execute(
            select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user_id)
        )
        return result.scalar() or 0
