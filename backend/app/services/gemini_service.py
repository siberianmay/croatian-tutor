"""Gemini AI service for multi-language learning."""

import asyncio
import json
import logging
from enum import Enum
from typing import Any

import google.generativeai as genai
from app.config import settings
from app.exceptions import GeminiParseError, GeminiRateLimitError, GeminiServiceError
from app.models.enums import CEFRLevel, Gender, PartOfSpeech
from google.api_core import exceptions as google_exceptions
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.0


class GeminiModel(str, Enum):
    gemini_2_0_fl = "gemini-2.0-flash"
    gemini_2_0_fl_lt = "gemini-2.0-flash-lite"
    gemini_2_5_fl_lt = "gemini-2.5-flash-lite"
    # gemini_2_5_fl_tts = "gemini-2.5-flash-tts"
    gemini_2_5_fl = "gemini-2.5-flash"
    gemini_2_5_pro = "gemini-2.5-pro"

    def __str__(self):
        return self._value_

    def __repr__(self):
        return self.__str__()


class GeminiService:
    """Service for interacting with Google Gemini API."""

    DEFAULT_MODEL = GeminiModel.gemini_2_5_fl

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")

        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Chat sessions keyed by session_key (e.g., "user_1_translation_cr_en")
        self._chat_sessions: dict[str, Any] = {}
        # Configured model name (can be set via set_model)
        self._configured_model: str | None = None

    def set_model(self, model_name: str) -> None:
        """Set the model to use for generation."""
        self._configured_model = model_name

    def _get_model(self, model_name: str | None = None) -> Any:
        """
        Get a GenerativeModel instance.

        Args:
            model_name: Optional model name override. If not provided,
                       uses configured model or default.
        """
        if model_name:
            return genai.GenerativeModel(model_name)
        if self._configured_model:
            return genai.GenerativeModel(self._configured_model)
        return genai.GenerativeModel(self.DEFAULT_MODEL.value)

    @property
    def _model(self) -> Any:
        """Get the default model instance."""
        return self._get_model()

    async def assess_word(self, word: str, language_name: str = "Croatian") -> dict[str, Any]:
        """
        Assess a word in the target language and return translation + metadata.

        Args:
            word: The word to assess in the target language
            language_name: Name of the language (e.g., "Croatian", "Italian")

        Returns:
            {
                "english": str,
                "part_of_speech": str,
                "gender": str | None,
                "cefr_level": str,
                "notes": str | None
            }
        """
        prompt = f"""Analyze this {language_name} word and provide information in JSON format.

Word: {word}

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
                "english": data.get("english", word),
                "part_of_speech": self._validate_pos(data.get("part_of_speech", "noun")),
                "gender": self._validate_gender(data.get("gender")),
                "cefr_level": self._validate_cefr(data.get("cefr_level", "A1")),
                "notes": data.get("notes"),
            }
        except Exception as e:
            logger.error(f"Failed to assess word '{word}' ({language_name}): {e}")
            # Return defaults on failure
            return {
                "english": "",
                "part_of_speech": "noun",
                "gender": None,
                "cefr_level": "A1",
                "notes": None,
            }

    async def assess_words_bulk(
        self,
        words: list[str],
        language_name: str = "Croatian",
        chunk_size: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Assess multiple words in the target language, processing in chunks.

        Args:
            words: List of words to assess in the target language
            language_name: Name of the language (e.g., "Croatian", "Italian")
            chunk_size: Number of words per Gemini API call (default: 10)
        """
        if not words:
            return []

        # Process words in chunks
        results: list[dict[str, Any]] = []
        for i in range(0, len(words), chunk_size):
            chunk = words[i : i + chunk_size]
            chunk_results = await self._assess_words_chunk(chunk, language_name)
            results.extend(chunk_results)
            logger.info(f"Processed chunk {i // chunk_size + 1}: {len(chunk)} words ({language_name})")

        return results

    async def _assess_words_chunk(
        self,
        words: list[str],
        language_name: str = "Croatian",
    ) -> list[dict[str, Any]]:
        """Assess a chunk of words in a single Gemini request."""
        words_list = "\n".join(f"- {w}" for w in words)
        prompt = f"""Analyze these {language_name} words and provide information for each.

Words:
{words_list}

Respond with ONLY a valid JSON array (no markdown, no explanation):
[
    {{
        "word": "original word",
        "english": "English translation",
        "part_of_speech": "noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection|numeral|particle|phrase",
        "gender": "masculine|feminine|neuter|null",
        "cefr_level": "A1|A2|B1|B2|C1|C2"
    }}
]

Important:
- Return one object per word in the same order
- gender is only for nouns, use null for other parts of speech
- cefr_level indicates difficulty for {language_name} learners"""

        try:
            response = await self._generate_bulk(prompt)
            data = self._parse_json(response)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array")

            results = []
            for i, item in enumerate(data):
                results.append(
                    {
                        "word": item.get("word", words[i] if i < len(words) else ""),
                        "english": item.get("english", ""),
                        "part_of_speech": self._validate_pos(item.get("part_of_speech", "noun")),
                        "gender": self._validate_gender(item.get("gender")),
                        "cefr_level": self._validate_cefr(item.get("cefr_level", "A1")),
                    }
                )
            return results
        except Exception as e:
            logger.error(f"Failed to assess chunk of {len(words)} {language_name} words: {e}")
            # Return empty assessments on failure
            return [
                {
                    "word": w,
                    "english": "",
                    "part_of_speech": "noun",
                    "gender": None,
                    "cefr_level": "A1",
                }
                for w in words
            ]

    async def generate_fill_in_blank(
        self,
        word: str,
        english: str,
        cefr_level: str,
        language_name: str = "Croatian",
    ) -> dict[str, str]:
        """
        Generate a fill-in-the-blank sentence for vocabulary practice.

        Args:
            word: The target word in the learning language
            english: English translation of the word
            cefr_level: CEFR difficulty level
            language_name: Name of the language (e.g., "Croatian", "Italian")

        Returns:
            {
                "sentence": "Ja volim ___.",
                "answer": "knjige",
                "hint": "books"
            }
        """
        prompt = f"""Create a fill-in-the-blank exercise for learning {language_name} vocabulary.

Target word: {word} (English: {english})
Difficulty level: {cefr_level}

Create a natural {language_name} sentence using this word, then replace the target word with "___".
The sentence should be appropriate for the {cefr_level} level.

Respond with ONLY valid JSON (no markdown):
{{
    "sentence": "{language_name} sentence with ___ where the word goes",
    "answer": "{word}",
    "hint": "Brief English hint to help the learner"
}}"""

        try:
            response = await self._generate(prompt)
            data = self._parse_json(response)
            return {
                "sentence": data.get("sentence", "___ ..."),
                "answer": data.get("answer", word),
                "hint": data.get("hint", english),
            }
        except Exception as e:
            logger.error(f"Failed to generate fill-in-blank for '{word}' ({language_name}): {e}")
            return {
                "sentence": "___ ...",
                "answer": word,
                "hint": english,
            }

    async def generate_fill_in_blank_batch(
        self,
        words: list[dict[str, str]],
        language_name: str = "Croatian",
    ) -> list[dict[str, str]]:
        """
        Generate fill-in-the-blank sentences for multiple words in a single API call.

        Args:
            words: List of dicts with 'word_id', 'word', 'english', 'cefr_level'
            language_name: Name of the language (e.g., "Croatian", "Italian")

        Returns:
            List of {word_id, sentence, answer, hint} for each word
        """
        if not words:
            return []

        words_list = "\n".join(
            f"- ID:{w['word_id']} | {w['word']} ({w['english']}) | Level: {w['cefr_level']}" for w in words
        )

        prompt = f"""Create fill-in-the-blank exercises for these {language_name} vocabulary words.

Words:
{words_list}

For each word, create a natural {language_name} sentence using that word, then replace it with "___".
Sentences should be appropriate for the word's CEFR level.

Respond with ONLY a valid JSON array (no markdown, no explanation):
[
    {{
        "word_id": <ID from the list>,
        "sentence": "{language_name} sentence with ___ where the word goes",
        "answer": "the {language_name} word",
        "hint": "Brief English hint"
    }}
]

Important:
- Return one object per word in the same order as the input
- Each sentence should be unique and natural
- Hints should help learners understand the context"""

        try:
            response = await self._generate_bulk(prompt)
            data = self._parse_json(response)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array")

            results = []
            for i, item in enumerate(data):
                word_data = words[i] if i < len(words) else {}
                results.append(
                    {
                        "word_id": item.get("word_id", word_data.get("word_id", 0)),
                        "sentence": item.get("sentence", "___ ..."),
                        "answer": item.get("answer", word_data.get("word", "")),
                        "hint": item.get("hint", word_data.get("english", "")),
                    }
                )
            return results
        except Exception as e:
            logger.error(f"Failed to generate fill-in-blank batch for {len(words)} {language_name} words: {e}")
            # Return fallback for all words
            return [
                {
                    "word_id": w["word_id"],
                    "sentence": "___ ...",
                    "answer": w["word"],
                    "hint": w["english"],
                }
                for w in words
            ]

    async def evaluate_answer(
        self,
        expected: str,
        user_answer: str,
        context: str = "",
        language_name: str = "Croatian",
    ) -> dict[str, Any]:
        """
        Evaluate a user's answer with AI assistance.

        Args:
            expected: The expected correct answer
            user_answer: The user's submitted answer
            context: Additional context about the exercise
            language_name: Name of the language (e.g., "Croatian", "Italian")

        Returns:
            {
                "correct": bool,
                "feedback": str,
                "corrections": list[str]
            }
        """
        prompt = f"""Evaluate this {language_name} language answer.

Expected answer: {expected}
User's answer: {user_answer}
Context: {context if context else "vocabulary exercise"}

Consider:
- Spelling (including any special characters or diacritics used in {language_name})
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
            logger.error(f"Failed to evaluate answer ({language_name}): {e}")
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
                # Check for blocked/empty responses before accessing .text
                if not response.candidates:
                    raise GeminiServiceError(
                        message="AI response was empty or blocked",
                        details={"prompt_preview": prompt[:200]},
                    )

                candidate = response.candidates[0]
                # finish_reason: 1=STOP (normal), 2=SAFETY, 3=RECITATION, 4=OTHER
                if candidate.finish_reason != 1:
                    reason_names = {2: "SAFETY", 3: "RECITATION", 4: "OTHER"}
                    reason = reason_names.get(candidate.finish_reason, f"UNKNOWN({candidate.finish_reason})")
                    logger.warning(f"Gemini response blocked: finish_reason={reason}")
                    raise GeminiServiceError(
                        message=f"AI response blocked due to {reason} filter",
                        details={"finish_reason": candidate.finish_reason},
                    )

                return response.text
            except GeminiServiceError:
                # Don't retry our own errors
                raise
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
                # Check for blocked/empty responses before accessing .text
                if not response.candidates:
                    raise GeminiServiceError(
                        message="AI chat response was empty or blocked",
                        details={"session_key": session_key},
                    )

                candidate = response.candidates[0]
                # finish_reason: 1=STOP (normal), 2=SAFETY, 3=RECITATION, 4=OTHER
                if candidate.finish_reason != 1:
                    reason_names = {2: "SAFETY", 3: "RECITATION", 4: "OTHER"}
                    reason = reason_names.get(candidate.finish_reason, f"UNKNOWN({candidate.finish_reason})")
                    logger.warning(f"Gemini chat response blocked: finish_reason={reason}")
                    raise GeminiServiceError(
                        message=f"AI chat response blocked due to {reason} filter",
                        details={"finish_reason": candidate.finish_reason},
                    )

                return response.text
            except GeminiServiceError:
                # Don't retry our own errors
                raise
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
