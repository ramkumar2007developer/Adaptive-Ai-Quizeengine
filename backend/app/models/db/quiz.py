"""
Quiz, Question, QuizAttempt Models — Core quiz engine entities.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    chapter: Mapped[str] = mapped_column(String(200), nullable=True)
    quiz_type: Mapped[str] = mapped_column(
        String(20), default="ADAPTIVE"
    )  # ADAPTIVE, PRACTICE, REVISION, CUSTOM
    total_questions: Mapped[int] = mapped_column(Integer, default=10)
    difficulty_start: Mapped[str] = mapped_column(String(20), default="Medium")
    current_difficulty: Mapped[str] = mapped_column(String(20), default="Medium")
    current_question_index: Mapped[int] = mapped_column(Integer, default=1)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    skill_score: Mapped[float] = mapped_column(Float, default=50.0)  # 0-100
    streak: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20), default="IN_PROGRESS"
    )  # IN_PROGRESS, COMPLETED, ABANDONED
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    user = relationship("User", back_populates="quizzes")
    document = relationship("Document", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", lazy="selectin")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, subject={self.subject}, status={self.status})>"


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(20), default="MCQ"
    )  # MCQ, TRUE_FALSE, FILL_BLANK, SHORT_ANSWER
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[list] = mapped_column(JSON, default=list)  # List of option strings
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer_index: Mapped[int] = mapped_column(Integer, nullable=True)  # For MCQ
    explanation: Mapped[str] = mapped_column(Text, default="")
    topic: Mapped[str] = mapped_column(String(200), default="", index=True)
    subtopic: Mapped[str] = mapped_column(String(200), default="")
    bloom_taxonomy: Mapped[str] = mapped_column(
        String(20), default="UNDERSTAND"
    )  # REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE, CREATE
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    estimated_difficulty_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 - 1.0
    confidence_score: Mapped[float] = mapped_column(Float, default=0.8)  # 0.0 - 1.0
    source_chunk_ids: Mapped[list] = mapped_column(JSON, default=list)  # Chunk UUIDs used for RAG
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    quiz = relationship("Quiz", back_populates="questions")
    attempt = relationship("QuizAttempt", back_populates="question", uselist=False, lazy="selectin")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, quiz={self.quiz_id}, num={self.question_number})>"


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    selected_answer: Mapped[str] = mapped_column(Text, default="")
    selected_index: Mapped[int] = mapped_column(Integer, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    response_time_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty_at_time: Mapped[str] = mapped_column(String(20), default="Medium")
    skill_score_at_time: Mapped[float] = mapped_column(Float, default=50.0)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    quiz = relationship("Quiz", back_populates="attempts")
    question = relationship("Question", back_populates="attempt")
    user = relationship("User", back_populates="attempts")

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, correct={self.is_correct})>"
