"""
Pydantic Schemas — Analytics & Recommendations endpoints.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============================================================
# Analytics Overview
# ============================================================

class OverviewStats(BaseModel):
    total_quizzes: int = 0
    total_questions_answered: int = 0
    overall_accuracy: float = 0.0
    overall_skill_score: float = 50.0
    mastery_level: str = "NOVICE"
    readiness_score: float = 0.0  # 0-100, exam preparedness
    avg_response_time: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    total_study_time_minutes: float = 0.0


class AnalyticsOverviewResponse(BaseModel):
    success: bool = True
    overview: OverviewStats


# ============================================================
# Topic-wise Analytics
# ============================================================

class TopicMasteryItem(BaseModel):
    topic: str
    subtopic: str = ""
    total_attempts: int
    correct_attempts: int
    accuracy: float
    avg_response_time: float
    skill_score: float
    mastery_level: str
    current_difficulty: str
    last_attempted: Optional[datetime] = None


class TopicAnalyticsResponse(BaseModel):
    success: bool = True
    topic_mastery: List[TopicMasteryItem]


# ============================================================
# Weak Areas
# ============================================================

class WeakAreaItem(BaseModel):
    topic: str
    subtopic: str = ""
    weakness_score: float
    reason: str
    suggested_action: str
    total_attempts: int
    incorrect_count: int
    avg_response_time: float


class WeakAreasResponse(BaseModel):
    success: bool = True
    weak_areas: List[WeakAreaItem]


# ============================================================
# Difficulty Distribution
# ============================================================

class DifficultyStats(BaseModel):
    difficulty: str
    total_questions: int
    correct_count: int
    accuracy: float
    avg_response_time: float


class DifficultyAnalyticsResponse(BaseModel):
    success: bool = True
    difficulty_stats: List[DifficultyStats]


# ============================================================
# Progress Over Time
# ============================================================

class ProgressDataPoint(BaseModel):
    date: str  # ISO date string
    quiz_id: str
    accuracy: float
    skill_score: float
    difficulty: str
    questions_answered: int


class ProgressResponse(BaseModel):
    success: bool = True
    data_points: List[ProgressDataPoint]


# ============================================================
# Recommendations
# ============================================================

class RecommendationItem(BaseModel):
    id: str
    recommendation_type: str
    title: str
    content: Dict[str, Any]
    priority: int
    is_completed: bool
    created_at: datetime


class RecommendationsResponse(BaseModel):
    success: bool = True
    recommendations: List[RecommendationItem]


# ============================================================
# Heatmap Data
# ============================================================

class HeatmapCell(BaseModel):
    topic: str
    difficulty: str
    accuracy: float
    attempts: int


class HeatmapResponse(BaseModel):
    success: bool = True
    cells: List[HeatmapCell]
