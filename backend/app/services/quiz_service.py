"""
Quiz Service — Orchestrates quiz creation, answer submission, and scoring.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.quiz_repository import QuizRepository
from app.repositories.user_repository import UserRepository
from app.services.difficulty_service import calculate_next_difficulty, calculate_score
from app.services.question_generator import get_question_generator
from app.models.schemas.quiz_schemas import (
    StartQuizRequest,
    QuizStartResponse,
    SubmitAnswerRequest,
    AnswerResponse,
    QuestionResponse
)

class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.quiz_repo = QuizRepository(db)
        self.user_repo = UserRepository(db)
        self.question_gen = get_question_generator()

    async def start_quiz(self, request: StartQuizRequest) -> QuizStartResponse:
        """Initialize a new quiz session and generate the first question."""
        
        user_id = request.user_id or "default_user"
        # Auto-ensure user exists in DB to prevent foreign key errors
        await self.user_repo.ensure_user_exists(user_id)

        # 1. Create Quiz Record
        quiz = await self.quiz_repo.create_quiz(
            user_id=user_id,
            subject=request.subject,
            chapter=request.chapter,
            document_id=request.document_id,
            difficulty_start=request.difficulty,
            current_difficulty=request.difficulty,
            total_questions=request.num_questions
        )

        # 2. Generate First Question
        doc_ids = [request.document_id] if request.document_id else None
        q_data = await self.question_gen.generate_question(
            topic=request.subject,
            difficulty=request.difficulty,
            use_rag=request.use_rag,
            document_ids=doc_ids
        )

        # 3. Save Question to DB
        question = await self.quiz_repo.create_question(
            quiz_id=quiz.id,
            question_number=1,
            question_type=q_data["question_type"],
            question_text=q_data["question_text"],
            options_json=q_data["options_json"],
            correct_answer=q_data["correct_answer"],
            correct_answer_index=q_data.get("correct_answer_index"),
            explanation=q_data["explanation"],
            topic=q_data["topic"],
            subtopic=q_data["subtopic"],
            bloom_taxonomy=q_data["bloom_taxonomy"],
            difficulty=q_data["difficulty"],
            estimated_difficulty_score=q_data["estimated_difficulty_score"],
            confidence_score=q_data["confidence_score"],
            source_chunk_ids=q_data["source_chunk_ids"]
        )

        # 4. Prepare Response
        q_response = QuestionResponse(
            id=question.id,
            question_number=question.question_number,
            question_type=question.question_type,
            difficulty=question.difficulty,
            question_text=question.question_text,
            options=question.options_json,
            topic=question.topic,
            subtopic=question.subtopic,
            bloom_taxonomy=question.bloom_taxonomy,
            estimated_difficulty_score=question.estimated_difficulty_score,
            confidence_score=question.confidence_score
        )

        return QuizStartResponse(
            success=True,
            quiz_id=quiz.id,
            subject=quiz.subject,
            current_difficulty=quiz.current_difficulty,
            question_number=1,
            total_questions=quiz.total_questions,
            skill_score=quiz.skill_score,
            question=q_response
        )

    async def submit_answer(self, request: SubmitAnswerRequest) -> AnswerResponse:
        """Process an answer, update scores, adapt difficulty, and generate next question."""
        user_id = request.user_id or "default_user"
        await self.user_repo.ensure_user_exists(user_id)

        quiz = await self.quiz_repo.get_quiz(request.quiz_id)
        if not quiz or quiz.status != "IN_PROGRESS":
            raise ValueError("Quiz not found or not in progress")

        question = await self.quiz_repo.get_question(request.question_id)
        if not question:
            raise ValueError("Question not found")

        # 1. Evaluate Answer
        is_correct = False
        if question.question_type == "MCQ":
            is_correct = request.selected_index == question.correct_answer_index
        else:
            # Simple string match for short answer
            is_correct = request.selected_answer.strip().lower() == question.correct_answer.strip().lower()

        # Calculate Score
        points = calculate_score(question.difficulty, request.response_time_seconds, is_correct)
        
        # Update Quiz State
        quiz.total_score += points
        quiz.streak = quiz.streak + 1 if is_correct else 0
        
        # Skill score update
        skill_delta = 2.0 if is_correct else -1.5
        if question.difficulty == "Hard": skill_delta *= 1.5
        quiz.skill_score = max(0.0, min(100.0, quiz.skill_score + skill_delta))

        # 2. Record Attempt
        await self.quiz_repo.create_attempt(
            quiz_id=quiz.id,
            question_id=question.id,
            user_id=user_id,
            selected_answer=request.selected_answer,
            selected_index=request.selected_index,
            is_correct=is_correct,
            response_time_seconds=request.response_time_seconds,
            difficulty_at_time=question.difficulty,
            skill_score_at_time=quiz.skill_score,
            points_awarded=points
        )

        # 3. Adaptive Difficulty Calculation
        history = await self.quiz_repo.get_quiz_attempts(quiz.id)
        history_dicts = [{"isCorrect": a.is_correct} for a in history]
        
        diff_shift = calculate_next_difficulty(quiz.current_difficulty, history_dicts)
        quiz.current_difficulty = diff_shift["nextDifficulty"]

        # 4. Check if complete
        is_completed = quiz.current_question_index >= quiz.total_questions
        next_q_response = None
        summary = None

        if is_completed:
            quiz.status = "COMPLETED"
            
            # Build Summary
            correct_count = sum(1 for a in history if a.is_correct) + (1 if is_correct else 0)
            
            # Fetch all questions for the quiz to build history
            questions = await self.quiz_repo.get_quiz_questions(quiz.id)
            q_map = {q.id: q for q in questions}
            
            history_data = []
            for a in history:
                q = q_map.get(a.question_id)
                if q:
                    history_data.append({
                        "question_number": q.question_number,
                        "difficulty": a.difficulty_at_time,
                        "points_awarded": a.points_awarded,
                        "question_text": q.question_text,
                        "explanation": q.explanation,
                        "is_correct": a.is_correct
                    })
            
            # Add the final attempt
            history_data.append({
                "question_number": question.question_number,
                "difficulty": question.difficulty,
                "points_awarded": points,
                "question_text": question.question_text,
                "explanation": question.explanation,
                "is_correct": is_correct
            })
            
            summary = {
                "total_score": quiz.total_score,
                "accuracy": (correct_count / quiz.total_questions) * 100,
                "final_skill_score": quiz.skill_score,
                "history": history_data
            }
        else:
            # Generate next question
            quiz.current_question_index += 1
            
            doc_ids = [quiz.document_id] if quiz.document_id else None
            use_rag = quiz.document_id is not None 

            q_data = await self.question_gen.generate_question(
                topic=quiz.subject,
                difficulty=quiz.current_difficulty,
                use_rag=use_rag,
                document_ids=doc_ids
            )
            
            next_question = await self.quiz_repo.create_question(
                quiz_id=quiz.id,
                question_number=quiz.current_question_index,
                question_type=q_data["question_type"],
                question_text=q_data["question_text"],
                options_json=q_data["options_json"],
                correct_answer=q_data["correct_answer"],
                correct_answer_index=q_data.get("correct_answer_index"),
                explanation=q_data["explanation"],
                topic=q_data["topic"],
                subtopic=q_data["subtopic"],
                bloom_taxonomy=q_data["bloom_taxonomy"],
                difficulty=q_data["difficulty"],
                estimated_difficulty_score=q_data["estimated_difficulty_score"],
                confidence_score=q_data["confidence_score"],
                source_chunk_ids=q_data["source_chunk_ids"]
            )
            
            next_q_response = QuestionResponse(
                id=next_question.id,
                question_number=next_question.question_number,
                question_type=next_question.question_type,
                difficulty=next_question.difficulty,
                question_text=next_question.question_text,
                options=next_question.options_json,
                topic=next_question.topic,
                subtopic=next_question.subtopic,
                bloom_taxonomy=next_question.bloom_taxonomy,
                estimated_difficulty_score=next_question.estimated_difficulty_score,
                confidence_score=next_question.confidence_score
            )

        await self.quiz_repo.update_quiz(quiz)

        return AnswerResponse(
            success=True,
            evaluation={
                "is_correct": is_correct,
                "correct_answer": question.correct_answer,
                "correct_answer_index": question.correct_answer_index,
                "explanation": question.explanation,
                "points_awarded": points,
                "total_score": quiz.total_score,
                "streak": quiz.streak,
                "skill_score": quiz.skill_score
            },
            difficulty_shift={
                "previous_difficulty": diff_shift.get("previousDifficulty", ""),
                "new_difficulty": diff_shift["nextDifficulty"],
                "changed": diff_shift["changed"],
                "direction": diff_shift.get("direction", "SAME"),
                "reason": diff_shift["reason"]
            },
            is_completed=is_completed,
            next_question=next_q_response,
            summary=summary
        )
