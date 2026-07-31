from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.services.quiz_service import QuizService
from app.models.schemas.quiz_schemas import (
    StartQuizRequest,
    QuizStartResponse,
    SubmitAnswerRequest,
    AnswerResponse
)

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])

# Static topics catalog — returned to the frontend topic selection page
AVAILABLE_TOPICS = [
    {"id": "dsa", "name": "Data Structures & Algorithms", "description": "Arrays, Trees, Graphs, Sorting, Searching, DP", "icon": "🌳"},
    {"id": "ml", "name": "Machine Learning", "description": "Supervised, Unsupervised Learning, Neural Networks, Deep Learning", "icon": "🤖"},
    {"id": "os", "name": "Operating Systems", "description": "Process Management, Memory, File Systems, Deadlocks", "icon": "💻"},
    {"id": "dbms", "name": "Database Management", "description": "SQL, Normalization, Transactions, Indexing, NoSQL", "icon": "🗄️"},
    {"id": "networking", "name": "Computer Networks", "description": "OSI Model, TCP/IP, HTTP, DNS, Security", "icon": "🌐"},
    {"id": "python", "name": "Python Programming", "description": "OOP, Generators, Decorators, Async, Libraries", "icon": "🐍"},
    {"id": "system_design", "name": "System Design", "description": "Scalability, Microservices, CAP Theorem, Caching", "icon": "🏗️"},
    {"id": "web", "name": "Web Development", "description": "HTML/CSS, JavaScript, React, REST APIs, Browsers", "icon": "🕸️"},
    {"id": "cloud", "name": "Cloud Computing", "description": "AWS/GCP/Azure, Containers, Kubernetes, Serverless", "icon": "☁️"},
    {"id": "security", "name": "Cybersecurity", "description": "Cryptography, Authentication, XSS, SQL Injection, OWASP", "icon": "🔐"},
]


@router.get("/topics")
async def get_topics():
    """Return the list of available quiz topics."""
    return {"topics": AVAILABLE_TOPICS}


@router.post("/start", response_model=QuizStartResponse)
async def start_quiz(request: StartQuizRequest, db: AsyncSession = Depends(get_db)):
    """Initialize a new quiz session."""
    quiz_service = QuizService(db)
    try:
        return await quiz_service.start_quiz(request)
    except Exception as e:
        print(f"[quiz_routes] Error starting quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(request: SubmitAnswerRequest, db: AsyncSession = Depends(get_db)):
    """Submit an answer and get evaluation + next question."""
    quiz_service = QuizService(db)
    try:
        return await quiz_service.submit_answer(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"[quiz_routes] Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
