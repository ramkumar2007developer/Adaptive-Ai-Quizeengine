import sys
import asyncio
import httpx
import uvicorn
import threading
import time

# Ensure UTF-8 output encoding for Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from app.main import app

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5002, log_level="error")

async def run_fastapi_tests():
    print("[TEST] Starting Python FastAPI Backend API & Adaptive Engine Tests...\n")
    
    # Launch server thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)  # Wait for uvicorn to boot

    base_url = "http://127.0.0.1:5002/api/quiz"
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health Check & Topics
        print("1. Testing GET /api/quiz/topics...")
        topics_res = await client.get(f"{base_url}/topics")
        topics_data = topics_res.json()
        print("   Status:", topics_res.status_code)
        print("   Topics received:", ", ".join([t["name"] for t in topics_data["topics"]]))
        assert topics_res.status_code == 200 and topics_data["success"]
        print("   [PASSED] Test 1 Passed!\n")

        # Test 2: Start Quiz Session
        print("2. Testing POST /api/quiz/start...")
        start_res = await client.post(
            f"{base_url}/start",
            json={"topic": "Data Structures & Algorithms", "initialDifficulty": "Medium"}
        )
        start_data = start_res.json()
        print("   Session ID:", start_data["sessionId"])
        print("   Initial Difficulty:", start_data["currentDifficulty"])
        print("   First Question:", start_data["question"]["question"])
        print("   Options:", start_data["question"]["options"])
        assert start_res.status_code == 200 and start_data["success"]
        print("   [PASSED] Test 2 Passed!\n")

        session_id = start_data["sessionId"]
        current_q = start_data["question"]

        # Test 3: Correct Answer Submission
        print("3. Testing POST /api/quiz/answer (Correct Answer)...")
        answer1_res = await client.post(
            f"{base_url}/answer",
            json={
                "sessionId": session_id,
                "selectedIndex": 1,
                "timeTakenSeconds": 4,
                "currentQuestionData": {
                    **current_q,
                    "correctAnswerIndex": 1,
                    "explanation": "BST search operates in logarithmic time."
                }
            }
        )
        answer1_data = answer1_res.json()
        print("   Answer Evaluation:", "CORRECT" if answer1_data["evaluation"]["isCorrect"] else "INCORRECT")
        print("   Points Awarded:", answer1_data["evaluation"]["pointsAwarded"])
        print("   Total Score:", answer1_data["evaluation"]["totalScore"])
        print("   Streak:", answer1_data["evaluation"]["streak"])
        print("   Difficulty Shift:", answer1_data["difficultyShift"]["reason"])
        assert answer1_res.status_code == 200 and answer1_data["evaluation"]["isCorrect"]
        print("   [PASSED] Test 3 Passed!\n")

        # Test 4: Adaptive Shift UP (Medium -> Hard)
        print("4. Testing Adaptive Difficulty Shift UP (Medium -> Hard)...")
        current_q = answer1_data["nextQuestion"]
        answer2_res = await client.post(
            f"{base_url}/answer",
            json={
                "sessionId": session_id,
                "selectedIndex": 2,
                "timeTakenSeconds": 5,
                "currentQuestionData": {
                    **current_q,
                    "correctAnswerIndex": 2,
                    "explanation": "Separate chaining maintains linked lists."
                }
            }
        )
        answer2_data = answer2_res.json()
        print("   Streak:", answer2_data["evaluation"]["streak"])
        print("   New Difficulty:", answer2_data["difficultyShift"]["newDifficulty"])
        print("   Shift Changed:", answer2_data["difficultyShift"]["changed"])
        print("   Shift Reason:", answer2_data["difficultyShift"]["reason"])
        assert answer2_data["difficultyShift"]["newDifficulty"] == "Hard"
        print("   [PASSED] Test 4 (Adaptive Shift UP to Hard) Passed!\n")

        # Test 5: Adaptive Shift DOWN (Hard -> Medium)
        print("5. Testing Adaptive Difficulty Shift DOWN (Hard -> Medium)...")
        current_q = answer2_data["nextQuestion"]
        wrong1_res = await client.post(
            f"{base_url}/answer",
            json={
                "sessionId": session_id,
                "selectedIndex": 0,
                "timeTakenSeconds": 10,
                "currentQuestionData": {**current_q, "correctAnswerIndex": 1, "explanation": "Test explanation"}
            }
        )
        wrong1_data = wrong1_res.json()

        wrong2_res = await client.post(
            f"{base_url}/answer",
            json={
                "sessionId": session_id,
                "selectedIndex": 0,
                "timeTakenSeconds": 10,
                "currentQuestionData": {**wrong1_data["nextQuestion"], "correctAnswerIndex": 1, "explanation": "Test explanation"}
            }
        )
        wrong2_data = wrong2_res.json()
        print("   New Difficulty after 2 errors:", wrong2_data["difficultyShift"]["newDifficulty"])
        print("   Shift Direction:", wrong2_data["difficultyShift"]["direction"])
        print("   Shift Reason:", wrong2_data["difficultyShift"]["reason"])
        assert wrong2_data["difficultyShift"]["newDifficulty"] == "Medium"
        print("   [PASSED] Test 5 (Adaptive Shift DOWN to Medium) Passed!\n")

    print("[SUCCESS] ALL FASTAPI BACKEND API & ADAPTIVE ENGINE TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_fastapi_tests())
