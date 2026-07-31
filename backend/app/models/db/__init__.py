"""DB Models Package — Import all models so Base.metadata discovers them."""
from app.models.db.user import User
from app.models.db.document import Document, DocumentChunk
from app.models.db.quiz import Quiz, Question, QuizAttempt
from app.models.db.analytics import UserTopicMastery, WeakTopic, LearningRecommendation

__all__ = [
    "User",
    "Document", "DocumentChunk",
    "Quiz", "Question", "QuizAttempt",
    "UserTopicMastery", "WeakTopic", "LearningRecommendation",
]
