"""
Question Generator Service — Uses LLM and optionally RAG context to generate questions.
Groq JSON mode requires the word 'JSON' in the system message body.
"""
import json
import uuid
import re
import traceback
from typing import Dict, Any, List, Optional

from app.services.llm_service import get_llm_service
from app.rag.rag_pipeline import retrieve_context, format_context_for_prompt

# -----------------------------------------------------------------
# Prompt template — the raw {{ }} curly braces in the JSON schema
# must be doubled so .format() doesn't choke on them.
# -----------------------------------------------------------------
QUESTION_GEN_SYSTEM = """You are an expert AI Assessment Engine and educator.
Generate ONE {difficulty} difficulty {question_type} question about the topic: "{topic}".
{context_block}
Rules:
- Question must be clear, accurate, factually correct, and unambiguous.
- For MCQ produce exactly 4 options. Place the correct answer at index {correct_index}.
- All options must be plausible but only ONE must be definitively correct.
- Bloom level should match difficulty: Easy=REMEMBER/UNDERSTAND, Medium=APPLY/ANALYZE, Hard=EVALUATE/CREATE.
- The "explanation" MUST be a comprehensive, educational explanation (3-5 sentences minimum) that:
  1. Clearly states WHY the correct answer is right with supporting facts/reasoning.
  2. Briefly explains why each incorrect option is wrong or misleading.
  3. Provides a key takeaway or real-world relevance of the concept.
- The "correct_answer" MUST exactly match the text of the option at "correct_answer_index".
- Return ONLY a JSON object — no markdown, no explanation outside JSON.

Required JSON schema:
{{
  "question_text": "Full question text here",
  "options": ["Option 0", "Option 1", "Option 2", "Option 3"],
  "correct_answer": "Exact text of the correct option (must match options[correct_answer_index])",
  "correct_answer_index": {correct_index},
  "explanation": "Detailed educational explanation: (1) Why the correct answer is right. (2) Why each wrong option is incorrect. (3) Key concept takeaway.",
  "subtopic": "Specific subtopic within the main topic",
  "bloom_taxonomy": "UNDERSTAND",
  "estimated_difficulty_score": 0.5
}}"""


class QuestionGenerator:
    def __init__(self):
        self.llm = get_llm_service()

    async def generate_question(
        self,
        topic: str,
        difficulty: str,
        question_type: str = "MCQ",
        document_ids: Optional[List[str]] = None,
        use_rag: bool = False,
    ) -> Dict[str, Any]:
        """Generate a single question, optionally using RAG-retrieved context."""

        context_block = ""
        source_chunk_ids = []

        # --- RAG retrieval ---
        if use_rag and document_ids:
            query = f"{topic} {difficulty} key concepts"
            try:
                retrieved_chunks = retrieve_context(
                    query=query, document_ids=document_ids, top_k=3
                )
                if retrieved_chunks:
                    context_text = format_context_for_prompt(retrieved_chunks)
                    source_chunk_ids = [
                        c.get("metadata", {}).get("chunk_id")
                        for c in retrieved_chunks
                        if c.get("metadata", {}).get("chunk_id")
                    ]
                    context_block = (
                        "CRITICAL: Base the question ONLY on the context below. "
                        "Do NOT use outside knowledge.\n\nContext:\n" + context_text
                    )
            except Exception as rag_err:
                print(f"[question_generator] RAG retrieval error: {rag_err}")

        # Pick a random correct index to avoid trivial index-0 bias
        import random
        correct_index = random.randint(0, 3) if question_type == "MCQ" else 0

        # --- Build system prompt ---
        system_prompt = QUESTION_GEN_SYSTEM.format(
            difficulty=difficulty,
            question_type=question_type,
            topic=topic,
            context_block=context_block,
            correct_index=correct_index,
        )

        user_prompt = (
            f"Generate a {difficulty} {question_type} question for the topic: {topic}. "
            "Respond with JSON only."
        )

        # --- Call LLM ---
        try:
            raw_response = await self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                json_mode=True,
            )
            parsed = self._parse_json(raw_response)

            if not parsed or not parsed.get("question_text"):
                raise ValueError("LLM returned empty/invalid JSON")

            return {
                "id": str(uuid.uuid4()),
                "question_number": 0,  # Set by quiz_service
                "question_type": question_type,
                "difficulty": difficulty,
                "question_text": parsed["question_text"],
                "options_json": parsed.get("options", []),
                "correct_answer": parsed.get("correct_answer", ""),
                "correct_answer_index": parsed.get("correct_answer_index", correct_index),
                "explanation": parsed.get("explanation", ""),
                "topic": topic,
                "subtopic": parsed.get("subtopic", ""),
                "bloom_taxonomy": parsed.get("bloom_taxonomy", "UNDERSTAND"),
                "estimated_difficulty_score": float(
                    parsed.get("estimated_difficulty_score", 0.5)
                ),
                "confidence_score": 0.9,
                "source_chunk_ids": source_chunk_ids,
            }

        except Exception as e:
            print(f"[question_generator] Generation failed: {e}")
            print(traceback.format_exc())
            return self._fallback(topic, difficulty)

    # ------------------------------------------------------------------
    def _parse_json(self, raw: str) -> dict:
        """Strip markdown fences and parse JSON."""
        text = raw.strip()
        # Remove ```json ... ``` or ``` ... ```
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            print(f"[question_generator] JSON parse error: {err} | raw: {text[:200]}")
            return {}

    def _fallback(self, topic: str, difficulty: str) -> dict:
        """Return a placeholder question when the LLM fails."""
        return {
            "id": str(uuid.uuid4()),
            "question_number": 0,
            "question_type": "MCQ",
            "difficulty": difficulty,
            "question_text": (
                f"[FALLBACK] Which of the following best describes a key concept in {topic}?"
            ),
            "options_json": [
                "It is a fundamental principle that governs the core behavior",
                "It is an unrelated concept from another domain",
                "It refers to an outdated methodology",
                "None of the above apply",
            ],
            "correct_answer": "It is a fundamental principle that governs the core behavior",
            "correct_answer_index": 0,
            "explanation": (
                f"This is a fallback question. The LLM could not generate a real question "
                f"for '{topic}' at '{difficulty}' level. Check your GROQ_API_KEY in .env."
            ),
            "topic": topic,
            "subtopic": "",
            "bloom_taxonomy": "REMEMBER",
            "estimated_difficulty_score": 0.5,
            "confidence_score": 0.1,
            "source_chunk_ids": [],
        }


def get_question_generator() -> QuestionGenerator:
    return QuestionGenerator()
