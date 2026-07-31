import time
import random
from typing import Dict, Any
from app.services.llm_service import generate_question

# In-memory session store
SESSIONS: Dict[str, Dict[str, Any]] = {}

AVAILABLE_TOPICS = [
    {
        "id": "dsa",
        "name": "Data Structures & Algorithms",
        "description": "Trees, Graphs, Sorting, Dynamic Programming & Big-O"
    },
    {
        "id": "webdev",
        "name": "Web Development & React",
        "description": "Modern JS, React Hooks, HTML5/CSS, DOM & Web Performance"
    },
    {
        "id": "ml",
        "name": "Machine Learning & AI",
        "description": "Neural Networks, Supervised/Unsupervised Learning & Transformers"
    }
]

def get_topics() -> list:
    return AVAILABLE_TOPICS

async def start_quiz_session(topic: str = "Data Structures & Algorithms", initial_difficulty: str = "Medium") -> dict:
    session_id = f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    initial_question = await generate_question(topic, initial_difficulty, 1)

    session_data = {
        "sessionId": session_id,
        "topic": topic,
        "currentDifficulty": initial_difficulty,
        "currentQuestionIndex": 1,
        "totalScore": 0,
        "history": [],
        "streak": 0
    }
    SESSIONS[session_id] = session_data

    return {
        "success": True,
        "sessionId": session_id,
        "topic": topic,
        "currentDifficulty": initial_difficulty,
        "questionNumber": 1,
        "totalQuestions": 10,
        "question": {
            "id": initial_question["id"],
            "difficulty": initial_question["difficulty"],
            "question": initial_question["question"],
            "options": initial_question["options"]
        }
    }

def get_session(session_id: str) -> dict:
    return SESSIONS.get(session_id)

def save_session(session_id: str, data: dict):
    SESSIONS[session_id] = data
