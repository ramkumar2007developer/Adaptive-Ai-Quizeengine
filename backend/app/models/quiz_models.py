from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class TopicModel(BaseModel):
    id: str
    name: str
    description: str

class TopicsResponse(BaseModel):
    success: bool = True
    topics: List[TopicModel]

class StartQuizRequest(BaseModel):
    topic: str = "Data Structures & Algorithms"
    initialDifficulty: str = "Medium"

class QuestionModel(BaseModel):
    id: str
    difficulty: str
    question: str
    options: List[str]
    correctAnswerIndex: Optional[int] = None
    explanation: Optional[str] = None

class QuizStartResponse(BaseModel):
    success: bool = True
    sessionId: str
    topic: str
    currentDifficulty: str
    questionNumber: int = 1
    totalQuestions: int = 10
    question: QuestionModel

class AnswerSubmissionRequest(BaseModel):
    sessionId: str
    selectedIndex: int
    timeTakenSeconds: int = 10
    currentQuestionData: QuestionModel

class EvaluationDetail(BaseModel):
    isCorrect: bool
    correctAnswerIndex: int
    explanation: str
    pointsAwarded: int
    totalScore: int
    streak: int

class DifficultyShiftDetail(BaseModel):
    previousDifficulty: str
    newDifficulty: str
    changed: bool
    direction: str = "SAME"
    reason: str

class AnswerSubmissionResponse(BaseModel):
    success: bool = True
    evaluation: EvaluationDetail
    difficultyShift: DifficultyShiftDetail
    isCompleted: bool = False
    nextQuestion: Optional[QuestionModel] = None
    summary: Optional[Dict[str, Any]] = None
