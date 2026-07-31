import json
import re

def format_question_response(raw_response: str, default_id: str = "q-1", expected_difficulty: str = "Medium") -> dict:
    """
    Sanitize and parse LLM generated JSON response
    """
    try:
        clean_text = raw_response.strip()
        # Remove markdown fences like ```json ... ```
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r"\s*```$", "", clean_text)

        parsed = json.loads(clean_text)

        options = parsed.get("options", [])
        if not isinstance(options, list) or len(options) != 4:
            options = ["Option A", "Option B", "Option C", "Option D"]

        return {
            "id": str(parsed.get("id", default_id)),
            "difficulty": str(parsed.get("difficulty", expected_difficulty)),
            "question": str(parsed.get("question", f"Sample {expected_difficulty} question regarding the topic")),
            "options": [str(opt) for opt in options],
            "correctAnswerIndex": int(parsed.get("correctAnswerIndex", 0)),
            "explanation": str(parsed.get("explanation", "Educational solution explanation."))
        }
    except Exception as err:
        print(f"[response_formatter] JSON parsing failed ({err}). Returning clean fallback structure.")
        return {
            "id": default_id,
            "difficulty": expected_difficulty,
            "question": f"Sample {expected_difficulty} question regarding the topic",
            "options": [
                "Correct answer demonstrating key concept",
                "Incorrect plausible distractor A",
                "Incorrect plausible distractor B",
                "Incorrect plausible distractor C"
            ],
            "correctAnswerIndex": 0,
            "explanation": f"This is a formatted question for {expected_difficulty} level."
        }
