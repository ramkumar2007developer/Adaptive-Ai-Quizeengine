"""
Pydantic Schemas — Request/Response models for User endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    display_name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    display_name: str
    created_at: datetime


class UserProfileResponse(BaseModel):
    success: bool = True
    user: UserResponse
    total_quizzes: int = 0
    total_questions_answered: int = 0
    overall_accuracy: float = 0.0
    overall_skill_score: float = 50.0
