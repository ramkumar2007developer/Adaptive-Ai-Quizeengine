import httpx
import asyncio

async def test_quiz_flow():
    base_url = "http://localhost:5000/api/quiz"
    
    print("\n--- 1. Testing Start Quiz without user_id (default fallback) ---")
    start_payload = {
        "topic": "Python Programming",
        "difficulty": "Medium",
        "num_questions": 5
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            res = await client.post(f"{base_url}/start", json=start_payload)
            print(f"Status Code: {res.status_code}")
            data = res.json()
            print("Response:", data)
            
            if not data.get("success"):
                print("Failed to start quiz!")
                return
                
            quiz_id = data["quiz_id"]
            question = data["question"]
            q_id = question["id"]
            
            print(f"\nQuiz Started! ID: {quiz_id}")
            print(f"Question 1 [{question['difficulty']}]: {question['question_text']}")
            if question.get("options"):
                for i, opt in enumerate(question["options"]):
                    print(f"  {i}) {opt}")
                    
            print("\n--- 2. Testing Answer Submission without user_id ---")
            answer_payload = {
                "quiz_id": quiz_id,
                "question_id": q_id,
                "selected_index": 0,
                "response_time_seconds": 8.0
            }
            
            res2 = await client.post(f"{base_url}/answer", json=answer_payload)
            print(f"Status Code: {res2.status_code}")
            data2 = res2.json()
            print("Evaluation Result:", data2.get("evaluation"))
            print("Difficulty Shift:", data2.get("difficulty_shift"))
            
            if data2.get("next_question"):
                next_q = data2["next_question"]
                print(f"\nNext Question [{next_q['difficulty']}]: {next_q['question_text']}")
                
        except Exception as e:
            print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_quiz_flow())
