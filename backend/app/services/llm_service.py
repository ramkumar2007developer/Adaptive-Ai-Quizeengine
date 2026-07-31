"""
LLM Service — Handles interactions with LLMs (Groq, Gemini) with structured JSON output.
"""
import os
import json
import random
import warnings
from typing import Dict, Any, List, Optional
from app.core.config import get_settings

# Suppress deprecation warnings from third-party SDKs
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    import groq
    from groq import AsyncGroq
except ImportError:
    groq = None

from app.utils.response_formatter import format_question_response


class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self.provider = self.settings.LLM_PROVIDER.lower()
        self.groq_client = None
        self.genai = None

        if self.provider == "groq" and self.settings.GROQ_API_KEY:
            if groq is None:
                print("[llm_service] WARNING: groq package not installed.")
            else:
                self.groq_client = AsyncGroq(api_key=self.settings.GROQ_API_KEY)
                print(f"[llm_service] Initialized Groq client with model {self.settings.GROQ_MODEL}")

        elif self.provider == "gemini" and self.settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.settings.GEMINI_API_KEY)
                self.genai = genai
                print("[llm_service] Initialized Gemini client")
            except ImportError:
                print("[llm_service] WARNING: google-generativeai package not installed.")

    async def generate(self, prompt: str, system_prompt: str = None, json_mode: bool = True) -> str:
        """Generic text generation from the configured provider."""
        if self.provider == "groq" and self.groq_client:
            return await self._generate_groq(prompt, system_prompt, json_mode)
        elif self.provider == "gemini" and self.genai:
            return await self._generate_gemini(prompt, system_prompt, json_mode)
        else:
            raise ValueError(f"LLM Provider '{self.provider}' is not properly configured.")

    async def _generate_groq(self, prompt: str, system_prompt: str = None, json_mode: bool = True) -> str:
        """Generate using Groq API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response_format = {"type": "json_object"} if json_mode else {"type": "text"}
        
        if json_mode and system_prompt and "json" not in system_prompt.lower():
            messages[0]["content"] += "\nRespond ONLY with valid JSON."
        elif json_mode and not system_prompt and "json" not in prompt.lower():
            messages[-1]["content"] += "\nRespond ONLY with valid JSON."

        completion = await self.groq_client.chat.completions.create(
            messages=messages,
            model=self.settings.GROQ_MODEL,
            response_format=response_format,
            temperature=0.2,
            max_tokens=1024,
        )
        return completion.choices[0].message.content

    async def _generate_gemini(self, prompt: str, system_prompt: str = None, json_mode: bool = True) -> str:
        """Generate using Gemini API."""
        model = self.genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt if system_prompt else None
        )
        
        if json_mode and "json" not in prompt.lower() and (not system_prompt or "json" not in system_prompt.lower()):
            prompt += "\n\nRespond ONLY with valid JSON."

        response = await model.generate_content_async(prompt)
        return response.text


def get_llm_service() -> LLMService:
    return LLMService()
