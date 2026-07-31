"""
User Model — Represents registered students/users.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    documents = relationship("Document", back_populates="user", lazy="selectin")
    quizzes = relationship("Quiz", back_populates="user", lazy="selectin")
    attempts = relationship("QuizAttempt", back_populates="user", lazy="selectin")
    topic_mastery = relationship("UserTopicMastery", back_populates="user", lazy="selectin")
    weak_topics = relationship("WeakTopic", back_populates="user", lazy="selectin")
    recommendations = relationship("LearningRecommendation", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
