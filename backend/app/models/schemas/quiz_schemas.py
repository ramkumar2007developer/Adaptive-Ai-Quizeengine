"""
Pydantic Schemas — Request/Response models for Quiz endpoints.
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Any, Dict
from datetime import datetime


# ============================================================
# Shared / Enums
# ============================================================

class TopicModel(BaseModel):
    id: str
    name: str
    description: str


# ============================================================
# Quiz Start
# ============================================================

class StartQuizRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    subject: Optional[str] = "Data Structures & Algorithms"
    topic: Optional[str] = None  # Support alias if user sends 'topic' instead of 'subject'
    chapter: Optional[str] = None
    document_id: Optional[str] = None
    difficulty: str = "Medium"
    num_questions: int = Field(default=10, ge=1, le=50)
    question_types: List[str] = Field(default=["MCQ"])  # MCQ, TRUE_FALSE, FILL_BLANK, SHORT_ANSWER
    use_rag: bool = False

    @model_validator(mode="after")
    def populate_subject_from_topic(self):
        if self.topic and (not self.subject or self.subject == "Data Structures & Algorithms"):
            self.subject = self.topic
        if not self.user_id:
            self.user_id = "default_user"
        return self


class QuestionResponse(BaseModel):
    id: str
    question_number: int
    question_type: str
    difficulty: str
    question_text: str
    options: Optional[List[str]] = None
    topic: str = ""
    subtopic: str = ""
    bloom_taxonomy: str = "UNDERSTAND"
    estimated_difficulty_score: float = 0.5
    confidence_score: float = 0.8


class QuizStartResponse(BaseModel):
    success: bool = True
    quiz_id: str
    subject: str
    current_difficulty: str
    question_number: int = 1
    total_questions: int = 10
    skill_score: float = 50.0
    question: QuestionResponse


# ============================================================
# Answer Submission
# ============================================================

class SubmitAnswerRequest(BaseModel):
    quiz_id: str
    question_id: str
    user_id: Optional[str] = "default_user"
    selected_answer: str = ""
    selected_index: Optional[int] = 0
    response_time_seconds: float = 10.0

    @model_validator(mode="after")
    def default_user_id(self):
        if not self.user_id:
            self.user_id = "default_user"
        return self


class EvaluationResult(BaseModel):
    is_correct: bool
    correct_answer: str
    correct_answer_index: Optional[int] = None
    explanation: str
    points_awarded: int
    total_score: int
    streak: int
    skill_score: float


class DifficultyShift(BaseModel):
    previous_difficulty: str
    new_difficulty: str
    changed: bool
    direction: str = "SAME"  # UP, DOWN, SAME
    reason: str


class AnswerResponse(BaseModel):
    success: bool = True
    evaluation: EvaluationResult
    difficulty_shift: DifficultyShift
    is_completed: bool = False
    next_question: Optional[QuestionResponse] = None
    summary: Optional[Dict[str, Any]] = None


# ============================================================
# Quiz History & Details
# ============================================================

class QuizSummary(BaseModel):
    quiz_id: str
    subject: str
    chapter: Optional[str] = None
    quiz_type: str
    total_questions: int
    questions_answered: int
    total_score: int
    accuracy_percentage: float
    skill_score: float
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None


class QuizHistoryResponse(BaseModel):
    success: bool = True
    total_quizzes: int
    quizzes: List[QuizSummary]


# ============================================================
# AI Features
# ============================================================

class GenerateHintRequest(BaseModel):
    question_id: str
    quiz_id: str


class HintResponse(BaseModel):
    success: bool = True
    hint: str
    hint_level: int = 1  # 1=subtle, 2=moderate, 3=strong


class ExplainAnswerRequest(BaseModel):
    question_id: str
    selected_answer: str


class ExplainAnswerResponse(BaseModel):
    success: bool = True
    why_wrong: str
    correct_concept: str
    comparison: str


class SimilarQuestionRequest(BaseModel):
    question_id: str
    difficulty: Optional[str] = None  # same, harder, easier


class SimilarQuestionResponse(BaseModel):
    success: bool = True
    question: QuestionResponse
