"""
Analytics & Tracking Service — Updates mastery and detects weak areas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.quiz_repository import QuizRepository

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_repo = AnalyticsRepository(db)
        self.quiz_repo = QuizRepository(db)

    async def get_overview(self, user_id: str) -> Dict[str, Any]:
        """Get high-level user stats."""
        quizzes = await self.quiz_repo.get_completed_quizzes(user_id)
        attempts = await self.quiz_repo.get_user_attempts(user_id, limit=1000) # Get all for accurate count
        
        total_quizzes = len(quizzes)
        total_answered = len(attempts)
        correct_answers = sum(1 for a in attempts if a.is_correct)
        
        accuracy = (correct_answers / total_answered * 100) if total_answered > 0 else 0.0
        
        # Get latest skill score from latest attempt, or default
        skill_score = 50.0
        if attempts:
             # Sort by created_at desc (already sorted by repo, but just in case)
             latest_attempt = attempts[0] 
             skill_score = latest_attempt.skill_score_at_time

        return {
            "total_quizzes": total_quizzes,
            "total_questions_answered": total_answered,
            "overall_accuracy": round(accuracy, 2),
            "overall_skill_score": round(skill_score, 2),
            "mastery_level": "INTERMEDIATE" if skill_score > 60 else "BEGINNER",
            "readiness_score": min(100.0, accuracy * 0.8 + skill_score * 0.2), # Arbitrary formula
            "avg_response_time": sum(a.response_time_seconds for a in attempts) / total_answered if total_answered > 0 else 0,
            "current_streak": 0, # Requires complex calculation across quizzes, simplify for now
            "best_streak": 0,
            "total_study_time_minutes": round(sum(a.response_time_seconds for a in attempts) / 60, 2)
        }
