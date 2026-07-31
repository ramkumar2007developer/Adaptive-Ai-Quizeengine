"""
Analytics Models — Topic mastery, weak areas, and learning recommendations.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserTopicMastery(Base):
    __tablename__ = "user_topic_mastery"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    subtopic: Mapped[str] = mapped_column(String(200), default="")
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_attempts: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 1.0
    avg_response_time: Mapped[float] = mapped_column(Float, default=0.0)  # seconds
    current_difficulty: Mapped[str] = mapped_column(String(20), default="Medium")
    skill_score: Mapped[float] = mapped_column(Float, default=50.0)  # 0 - 100
    mastery_level: Mapped[str] = mapped_column(
        String(20), default="NOVICE"
    )  # NOVICE, BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    last_attempted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user = relationship("User", back_populates="topic_mastery")

    def __repr__(self) -> str:
        return f"<UserTopicMastery(user={self.user_id}, topic={self.topic}, mastery={self.mastery_level})>"


class WeakTopic(Base):
    __tablename__ = "weak_topics"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    subtopic: Mapped[str] = mapped_column(String(200), default="")
    weakness_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 - 1.0 (higher = weaker)
    reason: Mapped[str] = mapped_column(Text, default="")
    suggested_action: Mapped[str] = mapped_column(Text, default="")
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time: Mapped[float] = mapped_column(Float, default=0.0)
    identified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user = relationship("User", back_populates="weak_topics")

    def __repr__(self) -> str:
        return f"<WeakTopic(user={self.user_id}, topic={self.topic}, score={self.weakness_score})>"


class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True
    )
    recommendation_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # REVISION, PRACTICE, STUDY_ORDER, DIFFICULTY_CHANGE
    title: Mapped[str] = mapped_column(String(300), default="")
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1 = highest
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user = relationship("User", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<LearningRecommendation(user={self.user_id}, type={self.recommendation_type})>"
