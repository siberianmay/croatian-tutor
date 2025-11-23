"""Gemini AI service for Croatian language learning."""

import asyncio
import json
import logging
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from google.generativeai.types import GenerationConfig

from app.config import settings
from app.exceptions import GeminiParseError, GeminiRateLimitError, GeminiServiceError
from app.models.enums import CEFRLevel, Gender, PartOfSpeech

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.0


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=settings.gemini_api_key)
        # Use gemini-2.0-flash for latest model
        self._model = genai.GenerativeModel("gemini-2.0-flash")
        # Chat sessions keyed by session_key (e.g., "user_1_translation_cr_en")
        self._chat_sessions: dict[str, Any] = {}

    async def assess_word(self, croatian_word: str) -> dict[str, Any]:
        """
        Assess a Croatian word and return translation + metadata.

        Returns:
            {
                "english": str,
                "part_of_speech": str,
                "gender": str | None,
                "cefr_level": str,
                "notes": str | None
            }
        """
        prompt = f"""Analyze this Croatian word and provide information in JSON format.

Word: {croatian_word}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
    "english": "English translation (most common meaning)",
    "part_of_speech": "noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection|numeral|particle|phrase",
    "gender": "masculine|feminine|neuter|null (only for nouns, null for other parts of speech)",
    "cefr_level": "A1|A2|B1|B2|C1|C2 (difficulty level for learners)",
    "notes": "Brief note about usage or common contexts (optional, can be null)"
}}"""

        try:
            response = await self._generate(prompt)
            data = self._parse_json(response)

            # Validate and normalize
            return {
                "english": data.get("english", croatian_word),
                "part_of_speech": self._validate_pos(data.get("part_of_speech", "noun")),
                "gender": self._validate_gender(data.get("gender")),
                "cefr_level": self._validate_cefr(data.get("cefr_level", "A1")),
                "notes": data.get("notes"),
            }
        except Exception as e:
            logger.error(f"Failed to assess word '{croatian_word}': {e}")
            # Return defaults on failure
            return {
                "english": "",
                "part_of_speech": "noun",
                "gender": None,
                "cefr_level": "A1",
                "notes": None,
            }

    async def assess_words_bulk(
        self, croatian_words: list[str], chunk_size: int = 10
    ) -> list[dict[str, Any]]:
        """
        Assess multiple Croatian words, processing in chunks to avoid API limits.

        Args:
            croatian_words: List of Croatian words to assess
            chunk_size: Number of words per Gemini API call (default: 10)
        """
        if not croatian_words:
            return []

        # Process words in chunks
        results: list[dict[str, Any]] = []
        for i in range(0, len(croatian_words), chunk_size):
            chunk = croatian_words[i:i + chunk_size]
            chunk_results = await self._assess_words_chunk(chunk)
            results.extend(chunk_results)
            logger.info(f"Processed chunk {i // chunk_size + 1}: {len(chunk)} words")

        return results

    async def _assess_words_chunk(
        self, croatian_words: list[str]
    ) -> list[dict[str, Any]]:
        """Assess a chunk of Croatian words in a single Gemini request."""
        words_list = "\n".join(f"- {w}" for w in croatian_words)
        prompt = f"""Analyze these Croatian words and provide information for each.

Words:
{words_list}

Respond with ONLY a valid JSON array (no markdown, no explanation):
[
    {{
        "croatian": "original word",
        "english": "English translation",
        "part_of_speech": "noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection|numeral|particle|phrase",
        "gender": "masculine|feminine|neuter|null",
        "cefr_level": "A1|A2|B1|B2|C1|C2"
    }}
]

Important:
- Return one object per word in the same order
- gender is only for nouns, use null for other parts of speech
- cefr_level indicates difficulty for Croatian learners"""

        try:
            response = await self._generate_bulk(prompt)
            data = self._parse_json(response)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array")

            results = []
            for i, item in enumerate(data):
                results.append({
                    "croatian": item.get("croatian", croatian_words[i] if i < len(croatian_words) else ""),
                    "english": item.get("english", ""),
                    "part_of_speech": self._validate_pos(item.get("part_of_speech", "noun")),
                    "gender": self._validate_gender(item.get("gender")),
                    "cefr_level": self._validate_cefr(item.get("cefr_level", "A1")),
                })
            return results
        except Exception as e:
            logger.error(f"Failed to assess chunk of {len(croatian_words)} words: {e}")
            # Return empty assessments on failure
            return [
                {
                    "croatian": w,
                    "english": "",
                    "part_of_speech": "noun",
                    "gender": None,
                    "cefr_level": "A1",
                }
                for w in croatian_words
            ]

    async def generate_fill_in_blank(
        self,
        word: str,
        english: str,
        cefr_level: str,
    ) -> dict[str, str]:
        """
        Generate a fill-in-the-blank sentence for vocabulary practice.

        Returns:
            {
                "sentence": "Ja volim ___.",
                "answer": "knjige",
                "hint": "books"
            }
        """
        prompt = f"""Create a fill-in-the-blank exercise for learning Croatian vocabulary.

Target word: {word} (English: {english})
Difficulty level: {cefr_level}

Create a natural Croatian sentence using this word, then replace the target word with "___".
The sentence should be appropriate for the {cefr_level} level.

Respond with ONLY valid JSON (no markdown):
{{
    "sentence": "Croatian sentence with ___ where the word goes",
    "answer": "{word}",
    "hint": "Brief English hint to help the learner"
}}"""

        try:
            response = await self._generate(prompt)
            data = self._parse_json(response)
            return {
                "sentence": data.get("sentence", f"___ je riječ."),
                "answer": data.get("answer", word),
                "hint": data.get("hint", english),
            }
        except Exception as e:
            logger.error(f"Failed to generate fill-in-blank for '{word}': {e}")
            return {
                "sentence": f"___ je hrvatska riječ.",
                "answer": word,
                "hint": english,
            }

    async def evaluate_answer(
        self,
        expected: str,
        user_answer: str,
        context: str = "",
    ) -> dict[str, Any]:
        """
        Evaluate a user's answer with AI assistance.

        Returns:
            {
                "correct": bool,
                "feedback": str,
                "corrections": list[str]
            }
        """
        prompt = f"""Evaluate this Croatian language answer.

Expected answer: {expected}
User's answer: {user_answer}
Context: {context if context else "vocabulary exercise"}

Consider:
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Minor typos vs incorrect answers
- Alternative valid forms

Respond with ONLY valid JSON:
{{
    "correct": true/false,
    "feedback": "Brief, encouraging feedback",
    "corrections": ["list", "of", "specific", "corrections"] or []
}}"""

        try:
            response = await self._generate(prompt)
            data = self._parse_json(response)
            return {
                "correct": bool(data.get("correct", False)),
                "feedback": data.get("feedback", ""),
                "corrections": data.get("corrections", []),
            }
        except Exception as e:
            logger.error(f"Failed to evaluate answer: {e}")
            # Fall back to exact match
            is_correct = expected.lower().strip() == user_answer.lower().strip()
            return {
                "correct": is_correct,
                "feedback": "Correct!" if is_correct else f"Expected: {expected}",
                "corrections": [] if is_correct else [f"Expected '{expected}'"],
            }

    async def _generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """
        Generate content from Gemini with retry logic.

        Raises:
            GeminiServiceError: On persistent failure after retries
            GeminiRateLimitError: On rate limit exceeded
        """
        config = GenerationConfig(
            temperature=0.3,
            max_output_tokens=max_tokens,
        )

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self._model.generate_content_async(
                    prompt,
                    generation_config=config,
                )
                return response.text
            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"Gemini rate limit hit (attempt {attempt + 1})")
                raise GeminiRateLimitError() from e
            except google_exceptions.GoogleAPIError as e:
                last_error = e
                logger.warning(f"Gemini API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected Gemini error (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        raise GeminiServiceError(
            message="AI service temporarily unavailable after retries",
            details={"error": str(last_error)},
        )

    async def _generate_bulk(self, prompt: str) -> str:
        """Generate content from Gemini with higher token limit for bulk operations."""
        return await self._generate(prompt, max_tokens=4096)

    # -------------------------------------------------------------------------
    # Chat Session Management
    # -------------------------------------------------------------------------

    def _get_or_create_chat(self, session_key: str, system_instruction: str = "") -> Any:
        """
        Get existing chat session or create a new one.

        Args:
            session_key: Unique key for this session (e.g., "user_1_grammar")
            system_instruction: Optional system prompt to set context for the chat

        Returns:
            ChatSession object with history preserved
        """
        if session_key not in self._chat_sessions:
            # Create new chat with optional system instruction as first message
            history = []
            if system_instruction:
                # Add system instruction as context
                history = [
                    {"role": "user", "parts": [system_instruction]},
                    {"role": "model", "parts": ["Understood. I'll follow these instructions."]},
                ]
            self._chat_sessions[session_key] = self._model.start_chat(history=history)
            logger.info(f"Created new chat session: {session_key}")

        return self._chat_sessions[session_key]

    async def generate_in_chat(
        self,
        session_key: str,
        prompt: str,
        system_instruction: str = "",
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate content within a persistent chat session.

        This maintains conversation history so Gemini won't repeat itself.

        Args:
            session_key: Unique key for this session
            prompt: The prompt to send
            system_instruction: System instruction for new sessions
            max_tokens: Maximum output tokens

        Returns:
            Generated text response
        """
        config = GenerationConfig(
            temperature=0.7,  # Higher temperature for more variety
            max_output_tokens=max_tokens,
        )

        chat = self._get_or_create_chat(session_key, system_instruction)

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await chat.send_message_async(
                    prompt,
                    generation_config=config,
                )
                return response.text
            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"Gemini rate limit hit in chat (attempt {attempt + 1})")
                raise GeminiRateLimitError() from e
            except google_exceptions.GoogleAPIError as e:
                last_error = e
                logger.warning(f"Gemini chat API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected Gemini chat error (attempt {attempt + 1}): {e}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY_SECONDS)

        raise GeminiServiceError(
            message="AI chat service temporarily unavailable after retries",
            details={"error": str(last_error)},
        )

    def end_chat_session(self, session_key: str) -> bool:
        """
        End and clear a chat session.

        Args:
            session_key: The session key to clear

        Returns:
            True if session was found and cleared, False if not found
        """
        if session_key in self._chat_sessions:
            del self._chat_sessions[session_key]
            logger.info(f"Ended chat session: {session_key}")
            return True
        return False

    def get_active_sessions(self) -> list[str]:
        """Return list of active session keys."""
        return list(self._chat_sessions.keys())

    def _parse_json(self, text: str) -> Any:
        """
        Parse JSON from Gemini response, handling markdown code blocks.

        Raises:
            GeminiParseError: When JSON parsing fails
        """
        # Strip markdown code blocks if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json) and last line (```)
            text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}, raw text: {text[:200]}")
            raise GeminiParseError(raw_response=text) from e

    def _validate_pos(self, pos: str | None) -> str:
        """Validate part of speech value."""
        valid = [e.value for e in PartOfSpeech]
        if pos and pos.lower() in valid:
            return pos.lower()
        return "noun"

    def _validate_gender(self, gender: str | None) -> str | None:
        """Validate gender value."""
        if gender is None or gender == "null":
            return None
        valid = [e.value for e in Gender]
        if gender.lower() in valid:
            return gender.lower()
        return None

    def _validate_cefr(self, level: str | None) -> str:
        """Validate CEFR level."""
        valid = [e.value for e in CEFRLevel]
        if level and level.upper() in valid:
            return level.upper()
        return "A1"


# Singleton instance
_gemini_service: GeminiService | None = None


def get_gemini_service() -> GeminiService:
    """Get or create the Gemini service singleton."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
