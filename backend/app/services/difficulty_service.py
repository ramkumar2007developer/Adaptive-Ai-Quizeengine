"""
Difficulty Service — Adaptive difficulty algorithms and scoring.
"""
from typing import List, Dict, Any

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard", "Very Hard"]

def calculate_next_difficulty(current_difficulty: str, history: List[Dict[str, Any]]) -> dict:
    """
    Advanced Adaptive Difficulty Algorithm:
    - Correct x3 -> Level Up
    - Wrong x2 -> Level Down
    """
    if not history:
        return {"nextDifficulty": current_difficulty, "changed": False, "reason": "Initial question baseline"}

    try:
        current_idx = DIFFICULTY_LEVELS.index(current_difficulty)
    except ValueError:
        current_idx = 1 # Default Medium

    recent_3 = history[-3:]
    recent_2 = history[-2:]

    consecutive_correct_3 = len(recent_3) == 3 and all(item.get("isCorrect") for item in recent_3)
    consecutive_incorrect_2 = len(recent_2) == 2 and all(not item.get("isCorrect") for item in recent_2)
    consecutive_correct_2 = len(recent_2) == 2 and all(item.get("isCorrect") for item in recent_2)

    # Level Up conditions
    if consecutive_correct_3 and current_idx < len(DIFFICULTY_LEVELS) - 1:
        return {
            "nextDifficulty": DIFFICULTY_LEVELS[current_idx + 1],
            "changed": True,
            "direction": "UP",
            "reason": "Excellent performance! 3 consecutive correct answers level up the difficulty."
        }
    
    # Fast track Easy -> Medium after 2 correct
    if current_difficulty == "Easy" and consecutive_correct_2:
        return {
            "nextDifficulty": "Medium",
            "changed": True,
            "direction": "UP",
            "reason": "Good job! Moving up to Medium difficulty."
        }

    # Level Down conditions
    if consecutive_incorrect_2 and current_idx > 0:
        return {
            "nextDifficulty": DIFFICULTY_LEVELS[current_idx - 1],
            "changed": True,
            "direction": "DOWN",
            "reason": "2 consecutive incorrect answers. Reducing difficulty to build fundamentals."
        }

    return {
        "nextDifficulty": current_difficulty,
        "changed": False,
        "direction": "SAME",
        "reason": "Maintaining current difficulty baseline."
    }

def calculate_score(difficulty: str, time_taken_seconds: float, is_correct: bool) -> int:
    """Calculate question score with speed bonus."""
    if not is_correct:
        return 0

    base_points = {
        "Easy": 10,
        "Medium": 20,
        "Hard": 30,
        "Very Hard": 40
    }.get(difficulty, 10)

    # Speed bonus (max 10 points)
    speed_bonus = max(0, 10 - int(time_taken_seconds)) if time_taken_seconds < 15 else 0
    return base_points + speed_bonus
