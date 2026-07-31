from app.controllers.quiz_controller import get_session, save_session
from app.services.difficulty_service import calculate_next_difficulty, calculate_score
from app.services.llm_service import generate_question

async def process_answer_submission(
    session_id: str,
    selected_index: int,
    time_taken_seconds: int,
    current_question_data: dict
) -> dict:
    session = get_session(session_id)
    if not session:
        return {"success": False, "message": "Quiz session expired or not found"}

    raw_correct = current_question_data.get("correctAnswerIndex")
    correct_index = raw_correct if isinstance(raw_correct, int) else 0
    is_correct = (selected_index == correct_index)

    points_awarded = calculate_score(session["currentDifficulty"], time_taken_seconds, is_correct)
    session["totalScore"] += points_awarded
    session["streak"] = session["streak"] + 1 if is_correct else 0

    history_item = {
        "questionNumber": session["currentQuestionIndex"],
        "difficulty": session["currentDifficulty"],
        "question": current_question_data.get("question", ""),
        "isCorrect": is_correct,
        "selectedIndex": selected_index,
        "correctIndex": correct_index,
        "pointsAwarded": points_awarded,
        "explanation": current_question_data.get("explanation", "No explanation provided.")
    }
    session["history"].append(history_item)

    # Adaptive shift
    adaptive_result = calculate_next_difficulty(session["currentDifficulty"], session["history"])
    prev_difficulty = session["currentDifficulty"]
    session["currentDifficulty"] = adaptive_result["nextDifficulty"]

    TOTAL_QUIZ_QUESTIONS = 10
    is_completed = session["currentQuestionIndex"] >= TOTAL_QUIZ_QUESTIONS

    next_question = None
    if not is_completed:
        session["currentQuestionIndex"] += 1
        next_question = await generate_question(session["topic"], session["currentDifficulty"], session["currentQuestionIndex"])

    save_session(session_id, session)

    correct_count = sum(1 for h in session["history"] if h["isCorrect"])
    summary = None
    if is_completed:
        summary = {
            "totalScore": session["totalScore"],
            "totalQuestions": TOTAL_QUIZ_QUESTIONS,
            "correctCount": correct_count,
            "accuracyPercentage": round((correct_count / TOTAL_QUIZ_QUESTIONS) * 100),
            "history": session["history"]
        }

    return {
        "success": True,
        "evaluation": {
            "isCorrect": is_correct,
            "correctAnswerIndex": correct_index,
            "explanation": current_question_data.get("explanation", "No explanation provided."),
            "pointsAwarded": points_awarded,
            "totalScore": session["totalScore"],
            "streak": session["streak"]
        },
        "difficultyShift": {
            "previousDifficulty": prev_difficulty,
            "newDifficulty": session["currentDifficulty"],
            "changed": adaptive_result["changed"],
            "direction": adaptive_result.get("direction", "SAME"),
            "reason": adaptive_result["reason"]
        },
        "isCompleted": is_completed,
        "nextQuestion": {
            "id": next_question["id"],
            "difficulty": next_question["difficulty"],
            "question": next_question["question"],
            "options": next_question["options"]
        } if next_question else None,
        "summary": summary
    }
