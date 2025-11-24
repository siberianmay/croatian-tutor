"""Exercise service for AI-powered language exercises."""

import logging
import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.grammar_topic import GrammarTopicCRUD, TopicProgressCRUD
from app.crud.session import SessionCRUD
from app.crud.word import WordCRUD
from app.models.enums import CEFRLevel, ErrorCategory, ExerciseType
from app.models.exercise_log import ExerciseLog
from app.models.error_log import ErrorLog
from app.models.session import Session
from app.services.gemini_service import GeminiService
from app.services.progress_service import ProgressService
from app.exceptions import GeminiServiceError

logger = logging.getLogger(__name__)


class ExerciseService:
    """Service for generating and evaluating AI-powered exercises."""

    def __init__(
        self,
        db: AsyncSession,
        gemini: GeminiService,
    ):
        self._db = db
        self._gemini = gemini
        self._topic_crud = GrammarTopicCRUD(db)
        self._progress_crud = TopicProgressCRUD(db)
        self._word_crud = WordCRUD(db)
        self._session_crud = SessionCRUD(db)
        self._progress_service = ProgressService(db)

    def _build_session_key(self, user_id: int, exercise_type: str, variant: str = "") -> str:
        """Build a unique session key for chat context."""
        if variant:
            return f"user_{user_id}_{exercise_type}_{variant}"
        return f"user_{user_id}_{exercise_type}"

    def end_exercise_chat_session(self, user_id: int, exercise_type: str, variant: str = "") -> bool:
        """
        End a chat session for a specific exercise type.

        Call this when user navigates away from an exercise page.
        """
        session_key = self._build_session_key(user_id, exercise_type, variant)
        return self._gemini.end_chat_session(session_key)

    async def _get_user_context(self, user_id: int) -> str:
        """Get comprehensive user context for Gemini prompts."""
        try:
            return await self._progress_service.build_gemini_context(user_id)
        except Exception as e:
            logger.warning(f"Failed to build user context: {e}")
            return ""

    async def _get_learnt_grammar_context(self, user_id: int) -> str:
        """Get a string describing the grammar topics the user has learned with mastery levels."""
        topics_with_mastery = await self._progress_crud.get_learnt_topics_with_mastery(user_id)
        if not topics_with_mastery:
            return ""

        # Build explicit topic list with IDs and mastery scores
        # Scale: 0-1000 (shown as percentage)
        topic_lines = []
        for t in topics_with_mastery:
            topic_id = t["topic_id"]
            mastery = t["mastery_score"]
            name = t["name"]
            pct = mastery // 10  # 0-100%

            # Simple level labels
            if mastery < 400:
                level = "WEAK"
            elif mastery < 800:
                level = "LEARNING"
            else:
                level = "STRONG"

            topic_lines.append(f"[ID:{topic_id}] '{name}' - {level} ({pct}%)")

        return f"""
USER'S GRAMMAR KNOWLEDGE (use ONLY these patterns, prioritize WEAK topics):
{chr(10).join(topic_lines)}"""

    async def _get_grammar_topics_for_exercise(self, user_id: int) -> tuple[str, dict[int, str]]:
        """
        Get grammar topics formatted for exercise generation.

        Returns:
            Tuple of (formatted context string, dict mapping topic_id -> topic_name)
        """
        topics_with_mastery = await self._progress_crud.get_learnt_topics_with_mastery(user_id)
        if not topics_with_mastery:
            return "", {}

        topic_lines = []
        topic_map: dict[int, str] = {}

        for t in topics_with_mastery:
            topic_id = t["topic_id"]
            name = t["name"]
            mastery = t["mastery_score"]
            pct = mastery // 10

            if mastery < 400:
                level = "WEAK"
            elif mastery < 800:
                level = "LEARNING"
            else:
                level = "STRONG"

            topic_lines.append(f"[ID:{topic_id}] '{name}' - {level} ({pct}%)")
            topic_map[topic_id] = name

        context = f"""
AVAILABLE GRAMMAR TOPICS (prioritize WEAK topics for practice):
{chr(10).join(topic_lines)}"""

        return context, topic_map

    # -------------------------------------------------------------------------
    # Conversation
    # -------------------------------------------------------------------------

    async def conversation_turn(
        self,
        user_id: int,
        message: str,
        history: list[dict[str, str]],
        cefr_level: CEFRLevel = CEFRLevel.A1,
    ) -> dict[str, Any]:
        """
        Process a conversation turn with the Croatian tutor.

        Returns:
            {
                "response": str,
                "corrections": [{"original": str, "corrected": str, "explanation": str}] | None,
                "new_vocabulary": [str] | None
            }
        """
        # Build conversation context
        history_text = "\n".join(
            f"{'User' if h['role'] == 'user' else 'Tutor'}: {h['content']}"
            for h in history[-10:]  # Last 10 turns for context
        )

        grammar_context = await self._get_learnt_grammar_context(user_id)
        user_context = await self._get_user_context(user_id)

        prompt = f"""You are a friendly Croatian language tutor.

{user_context}
{grammar_context}

Conversation so far:
{history_text}

User: {message}

Respond in a helpful, encouraging way. If the user writes in Croatian:
1. Correct any grammar or spelling mistakes
2. Provide the natural way to express their thought
3. Introduce new vocabulary when appropriate

If the user writes in English, respond primarily in Croatian with English explanations as needed.
Tailor your responses to the student's level and focus on their weak areas when appropriate.

Respond with ONLY valid JSON:
{{
    "response": "Your response to the user (mix Croatian and English as appropriate for their level)",
    "corrections": [
        {{"original": "what they wrote", "corrected": "correct form", "explanation": "brief explanation"}}
    ] or null if no corrections needed,
    "new_vocabulary": ["croatian_word1", "croatian_word2"] or null if no new words introduced
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            # Log any errors found for pattern tracking
            if data.get("corrections"):
                for correction in data["corrections"]:
                    await self._log_error(
                        user_id=user_id,
                        category=ErrorCategory.OTHER,  # Could be smarter categorization
                        details=correction.get("original"),
                        correction=correction.get("corrected"),
                    )

            return {
                "response": data.get("response", "Oprostite, nisam razumio."),
                "corrections": data.get("corrections"),
                "new_vocabulary": data.get("new_vocabulary"),
            }
        except Exception as e:
            logger.error(f"Conversation turn failed: {e}")
            return {
                "response": "Oprostite, došlo je do greške. Možete li ponoviti?",
                "corrections": None,
                "new_vocabulary": None,
            }

    # -------------------------------------------------------------------------
    # Grammar Exercises
    # -------------------------------------------------------------------------

    async def generate_grammar_exercise(
        self,
        user_id: int,
        topic_id: int | None = None,
        cefr_level: CEFRLevel | None = None,
    ) -> dict[str, Any]:
        """
        Generate a grammar exercise.

        Gemini selects which topic to test based on mastery levels (prioritizing weak topics).
        The selected topic_id is returned for progress tracking.

        Returns:
            {
                "exercise_id": str,
                "topic_id": int,
                "topic_name": str,
                "instruction": str,
                "question": str,
                "hints": [str] | None,
                "expected_answer": str
            }
        """
        # Get all learnt topics with their IDs and mastery
        grammar_context, topic_map = await self._get_grammar_topics_for_exercise(user_id)

        if not topic_map:
            return {
                "exercise_id": "",
                "topic_id": 0,
                "topic_name": "No topics available",
                "instruction": "Please add and mark some grammar topics as learnt first.",
                "question": "",
                "hints": None,
                "expected_answer": "",
            }

        user_context = await self._get_user_context(user_id)
        session_key = self._build_session_key(user_id, "grammar")

        # System instruction
        system_instruction = f"""You are a Croatian grammar exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE exercises each time - never repeat
2. Prioritize WEAK topics - they need more practice
3. Always respond with ONLY valid JSON
4. Include the topic_id from the list above"""

        # Prompt asking Gemini to select topic and generate exercise
        prompt = f"""Generate a NEW grammar exercise.

Choose ONE topic from the list above (prioritize WEAK topics) and create an exercise for it.
You MUST return the topic_id from the list.

Respond with ONLY valid JSON:
{{
    "topic_id": <number from the topic list>,
    "instruction": "Clear instruction in English",
    "question": "The exercise question in Croatian",
    "hints": ["hint1", "hint2"] or null,
    "expected_answer": "The correct answer"
}}"""

        try:
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
            data = self._gemini._parse_json(response_text)

            # Validate topic_id from Gemini's response
            returned_topic_id = data.get("topic_id")
            if returned_topic_id and returned_topic_id in topic_map:
                selected_topic_id = returned_topic_id
                selected_topic_name = topic_map[returned_topic_id]
            else:
                # Fallback to first (weakest) topic if Gemini returns invalid ID
                selected_topic_id = next(iter(topic_map.keys()))
                selected_topic_name = topic_map[selected_topic_id]
                logger.warning(f"Gemini returned invalid topic_id {returned_topic_id}, using {selected_topic_id}")

            return {
                "exercise_id": str(uuid.uuid4()),
                "topic_id": selected_topic_id,
                "topic_name": selected_topic_name,
                "instruction": data.get("instruction", "Complete the exercise."),
                "question": data.get("question", ""),
                "hints": data.get("hints"),
                "expected_answer": data.get("expected_answer", ""),
            }
        except GeminiServiceError:
            # Re-raise Gemini errors to be handled by exception handler
            raise
        except Exception as e:
            logger.error(f"Grammar exercise generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate grammar exercise: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    async def generate_grammar_exercises_batch(
        self,
        user_id: int,
        count: int = 10,
        cefr_level: CEFRLevel | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate multiple grammar exercises in a single API call.

        Args:
            user_id: User ID
            count: Number of exercises to generate (default 10)
            cefr_level: Optional CEFR level filter

        Returns:
            List of exercise dicts with topic_id, instruction, question, hints, expected_answer
        """
        grammar_context, topic_map = await self._get_grammar_topics_for_exercise(user_id)

        if not topic_map:
            return []

        user_context = await self._get_user_context(user_id)
        topic_ids_str = ", ".join(str(tid) for tid in topic_map.keys())

        prompt = f"""Generate {count} unique grammar exercises for Croatian language learning.

{user_context}
{grammar_context}

Available topic IDs: [{topic_ids_str}]

CRITICAL RULES:
1. Generate EXACTLY {count} unique exercises - NO REPETITION
2. Each exercise should test a DIFFERENT grammar concept
3. Prioritize WEAK topics from the list above
4. Include the topic_id for each exercise
5. Vary the exercise types (fill-in-blank, transformation, correction, etc.)

Respond with ONLY a valid JSON array (no markdown):
[
    {{
        "topic_id": <number from available IDs>,
        "instruction": "Clear instruction in English",
        "question": "The exercise question in Croatian",
        "hints": ["hint1", "hint2"] or null,
        "expected_answer": "The correct answer"
    }}
]

Return exactly {count} objects."""

        try:
            response_text = await self._gemini._generate_bulk(prompt)
            data = self._gemini._parse_json(response_text)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array")

            results = []
            for item in data[:count]:
                returned_topic_id = item.get("topic_id")
                if returned_topic_id and returned_topic_id in topic_map:
                    selected_topic_id = returned_topic_id
                    selected_topic_name = topic_map[returned_topic_id]
                else:
                    selected_topic_id = next(iter(topic_map.keys()))
                    selected_topic_name = topic_map[selected_topic_id]

                results.append({
                    "exercise_id": str(uuid.uuid4()),
                    "topic_id": selected_topic_id,
                    "topic_name": selected_topic_name,
                    "instruction": item.get("instruction", "Complete the exercise."),
                    "question": item.get("question", ""),
                    "hints": item.get("hints"),
                    "expected_answer": item.get("expected_answer", ""),
                })

            return results
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Grammar batch generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate grammar exercises batch: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    async def evaluate_grammar_answers_batch(
        self,
        user_id: int,
        answers: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Evaluate multiple grammar answers in a single API call.

        Args:
            user_id: User ID
            answers: List of dicts with user_answer, expected_answer, question, topic_id

        Returns:
            List of evaluation results with correct, score, feedback, error_category, topic_id
        """
        if not answers:
            return []

        user_context = await self._get_user_context(user_id)

        answers_text = "\n".join(
            f"{i+1}. Question: {a['question']}\n"
            f"   Expected: {a['expected_answer']}\n"
            f"   User answered: {a['user_answer']}"
            for i, a in enumerate(answers)
        )

        prompt = f"""Evaluate these Croatian grammar exercise answers.

{user_context}

ANSWERS TO EVALUATE:
{answers_text}

Consider for each:
- Grammar accuracy (cases, conjugations, agreements)
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Alternative valid forms
- Partial credit for mostly correct answers

Respond with ONLY valid JSON - an array with one evaluation object per answer:
[
    {{
        "correct": true/false,
        "score": 0.0 to 1.0,
        "feedback": "Brief, encouraging feedback",
        "error_category": "case_error|gender_agreement|verb_conjugation|word_order|spelling|vocabulary|accent|other|null"
    }}
]

Return exactly {len(answers)} objects in the same order."""

        try:
            response_text = await self._gemini._generate_bulk(prompt)
            data = self._gemini._parse_json(response_text)

            if not isinstance(data, list):
                data = [data]

            results = []
            for i, answer in enumerate(answers):
                if i < len(data):
                    item = data[i]
                    correct = bool(item.get("correct", False))
                    score = float(item.get("score", 1.0 if correct else 0.0))
                    error_cat = item.get("error_category")
                    if error_cat == "null":
                        error_cat = None

                    topic_id = answer.get("topic_id")
                    if error_cat and not correct and topic_id:
                        try:
                            category = ErrorCategory(error_cat)
                        except ValueError:
                            category = ErrorCategory.OTHER

                        await self._log_error(
                            user_id=user_id,
                            category=category,
                            topic_id=topic_id,
                            details=answer["user_answer"],
                            correction=answer["expected_answer"],
                        )

                    if topic_id:
                        await self._progress_crud.update_progress(
                            user_id=user_id,
                            topic_id=topic_id,
                            correct=correct,
                        )

                    results.append({
                        "correct": correct,
                        "score": score,
                        "feedback": item.get("feedback", ""),
                        "error_category": error_cat,
                        "topic_id": topic_id,
                    })
                else:
                    is_correct = answer["expected_answer"].lower().strip() == answer["user_answer"].lower().strip()
                    results.append({
                        "correct": is_correct,
                        "score": 1.0 if is_correct else 0.0,
                        "feedback": "Correct!" if is_correct else f"Expected: {answer['expected_answer']}",
                        "error_category": None,
                        "topic_id": answer.get("topic_id"),
                    })

            return results
        except Exception as e:
            logger.error(f"Grammar batch evaluation failed: {e}")
            return [
                {
                    "correct": a["expected_answer"].lower().strip() == a["user_answer"].lower().strip(),
                    "score": 1.0 if a["expected_answer"].lower().strip() == a["user_answer"].lower().strip() else 0.0,
                    "feedback": "Correct!" if a["expected_answer"].lower().strip() == a["user_answer"].lower().strip() else f"Expected: {a['expected_answer']}",
                    "error_category": None,
                    "topic_id": a.get("topic_id"),
                }
                for a in answers
            ]

    # -------------------------------------------------------------------------
    # Translation Exercises
    # -------------------------------------------------------------------------

    async def generate_translation_exercise(
        self,
        user_id: int,
        direction: str,  # "cr_en" or "en_cr"
        cefr_level: CEFRLevel = CEFRLevel.A1,
        recent_sentences: list[str] | None = None,  # Kept for API compatibility, but chat handles history
    ) -> dict[str, Any]:
        """
        Generate a translation exercise.

        Returns:
            {
                "exercise_id": str,
                "topic_id": int | None,
                "topic_name": str | None,
                "source_text": str,
                "source_language": str,
                "target_language": str,
                "expected_answer": str
            }
        """
        if direction == "cr_en":
            source_lang = "Croatian"
            target_lang = "English"
        else:
            source_lang = "English"
            target_lang = "Croatian"

        # Get grammar topics for progress tracking
        grammar_context, topic_map = await self._get_grammar_topics_for_exercise(user_id)
        user_context = await self._get_user_context(user_id)

        # Build session key - separate sessions for each direction
        session_key = self._build_session_key(user_id, "translation", direction)

        # System instruction for translation exercise generation
        system_instruction = f"""You are a Croatian translation exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE sentences each time - NEVER repeat a sentence you've already given
2. Vary vocabulary, topics, and sentence complexity
3. Always respond with ONLY valid JSON (no markdown, no explanation)
4. Remember all sentences from this conversation to avoid repetition
5. Include the topic_id of the PRIMARY grammar concept being practiced"""

        prompt = f"""Generate a NEW translation exercise (completely different from any previous ones).

Direction: {source_lang} → {target_lang}
CEFR Level: {cefr_level.value}

Create a sentence appropriate for this level that practices a grammar topic from the list above.
Prioritize WEAK topics to help the user improve.

Respond with ONLY valid JSON:
{{
    "topic_id": <number from the topic list - the PRIMARY grammar concept in this sentence>,
    "source_text": "The sentence in {source_lang}",
    "expected_answer": "The correct translation in {target_lang}"
}}"""

        try:
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
            data = self._gemini._parse_json(response_text)

            # Validate topic_id from Gemini's response
            returned_topic_id = data.get("topic_id")
            if returned_topic_id and topic_map and returned_topic_id in topic_map:
                selected_topic_id = returned_topic_id
                selected_topic_name = topic_map[returned_topic_id]
            else:
                # No valid topic - user may not have any learnt topics
                selected_topic_id = None
                selected_topic_name = None

            return {
                "exercise_id": str(uuid.uuid4()),
                "topic_id": selected_topic_id,
                "topic_name": selected_topic_name,
                "source_text": data.get("source_text", ""),
                "source_language": source_lang,
                "target_language": target_lang,
                "expected_answer": data.get("expected_answer", ""),
            }
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Translation exercise generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate translation exercise: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    async def generate_translation_exercises_batch(
        self,
        user_id: int,
        direction: str,
        count: int = 10,
        cefr_level: CEFRLevel = CEFRLevel.A1,
    ) -> list[dict[str, Any]]:
        """
        Generate multiple translation exercises in a single API call.

        Args:
            user_id: User ID
            direction: "cr_en" or "en_cr"
            count: Number of exercises to generate (default 10)
            cefr_level: CEFR level for the exercises

        Returns:
            List of exercise dicts with:
            - exercise_id: str
            - topic_id: int | None
            - source_text: str
            - source_language: str
            - target_language: str
            - expected_answer: str
        """
        if direction == "cr_en":
            source_lang = "Croatian"
            target_lang = "English"
        else:
            source_lang = "English"
            target_lang = "Croatian"

        # Get grammar topics for progress tracking
        grammar_context, topic_map = await self._get_grammar_topics_for_exercise(user_id)
        user_context = await self._get_user_context(user_id)

        # Format topic IDs for the prompt
        topic_ids_str = ", ".join(str(tid) for tid in topic_map.keys()) if topic_map else "none"

        prompt = f"""Generate {count} unique translation exercises for Croatian language learning.

{user_context}
{grammar_context}

Direction: {source_lang} → {target_lang}
CEFR Level: {cefr_level.value}
Available topic IDs: [{topic_ids_str}]

CRITICAL RULES:
1. Generate EXACTLY {count} unique sentences - NO REPETITION
2. Vary vocabulary, topics, and sentence structures
3. Each sentence should practice a different grammar concept if possible
4. Prioritize WEAK topics from the list above
5. Include topic_id for the PRIMARY grammar concept in each sentence

Respond with ONLY a valid JSON array (no markdown):
[
    {{
        "topic_id": <number from available IDs or null if no grammar topic>,
        "source_text": "The sentence in {source_lang}",
        "expected_answer": "The correct translation in {target_lang}"
    }}
]

Return exactly {count} objects."""

        try:
            response_text = await self._gemini._generate_bulk(prompt)
            data = self._gemini._parse_json(response_text)

            if not isinstance(data, list):
                raise ValueError("Expected JSON array")

            results = []
            for i, item in enumerate(data[:count]):
                # Validate topic_id
                returned_topic_id = item.get("topic_id")
                if returned_topic_id and topic_map and returned_topic_id in topic_map:
                    selected_topic_id = returned_topic_id
                    selected_topic_name = topic_map[returned_topic_id]
                else:
                    selected_topic_id = None
                    selected_topic_name = None

                results.append({
                    "exercise_id": str(uuid.uuid4()),
                    "topic_id": selected_topic_id,
                    "topic_name": selected_topic_name,
                    "source_text": item.get("source_text", ""),
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "expected_answer": item.get("expected_answer", ""),
                })

            return results
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Translation batch generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate translation exercises batch: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    async def evaluate_translation_answers_batch(
        self,
        user_id: int,
        answers: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Evaluate multiple translation answers in a single API call.

        Args:
            user_id: User ID
            answers: List of dicts with:
                - user_answer: str
                - expected_answer: str
                - source_text: str
                - topic_id: int | None

        Returns:
            List of evaluation results with:
            - correct: bool
            - score: float
            - feedback: str
            - error_category: str | None
            - topic_id: int | None (echoed back for progress tracking)
        """
        if not answers:
            return []

        user_context = await self._get_user_context(user_id)

        # Build answers list for prompt
        answers_text = "\n".join(
            f"{i+1}. Source: {a['source_text']}\n"
            f"   Expected: {a['expected_answer']}\n"
            f"   User answered: {a['user_answer']}"
            for i, a in enumerate(answers)
        )

        prompt = f"""Evaluate these Croatian translation exercise answers.

{user_context}

ANSWERS TO EVALUATE:
{answers_text}

Consider for each:
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Grammar accuracy
- Alternative valid phrasings
- Partial credit for mostly correct answers

Respond with ONLY valid JSON - an array with one evaluation object per answer:
[
    {{
        "correct": true/false,
        "score": 0.0 to 1.0,
        "feedback": "Brief, encouraging feedback",
        "error_category": "case_error|gender_agreement|verb_conjugation|word_order|spelling|vocabulary|accent|other|null"
    }}
]

Return exactly {len(answers)} objects in the same order."""

        try:
            response_text = await self._gemini._generate_bulk(prompt)
            data = self._gemini._parse_json(response_text)

            if not isinstance(data, list):
                data = [data]

            results = []
            for i, answer in enumerate(answers):
                if i < len(data):
                    item = data[i]
                    correct = bool(item.get("correct", False))
                    score = float(item.get("score", 1.0 if correct else 0.0))
                    error_cat = item.get("error_category")
                    if error_cat == "null":
                        error_cat = None

                    # Log error if present
                    topic_id = answer.get("topic_id")
                    if error_cat and not correct and topic_id:
                        try:
                            category = ErrorCategory(error_cat)
                        except ValueError:
                            category = ErrorCategory.OTHER

                        await self._log_error(
                            user_id=user_id,
                            category=category,
                            topic_id=topic_id,
                            details=answer["user_answer"],
                            correction=answer["expected_answer"],
                        )

                    # Update topic progress
                    if topic_id:
                        await self._progress_crud.update_progress(
                            user_id=user_id,
                            topic_id=topic_id,
                            correct=correct,
                        )

                    results.append({
                        "correct": correct,
                        "score": score,
                        "feedback": item.get("feedback", ""),
                        "error_category": error_cat,
                        "topic_id": topic_id,
                    })
                else:
                    # Fallback for missing evaluations
                    is_correct = answer["expected_answer"].lower().strip() == answer["user_answer"].lower().strip()
                    results.append({
                        "correct": is_correct,
                        "score": 1.0 if is_correct else 0.0,
                        "feedback": "Correct!" if is_correct else f"Expected: {answer['expected_answer']}",
                        "error_category": None,
                        "topic_id": answer.get("topic_id"),
                    })

            return results
        except Exception as e:
            logger.error(f"Translation batch evaluation failed: {e}")
            # Fall back to exact match for all
            return [
                {
                    "correct": a["expected_answer"].lower().strip() == a["user_answer"].lower().strip(),
                    "score": 1.0 if a["expected_answer"].lower().strip() == a["user_answer"].lower().strip() else 0.0,
                    "feedback": "Correct!" if a["expected_answer"].lower().strip() == a["user_answer"].lower().strip() else f"Expected: {a['expected_answer']}",
                    "error_category": None,
                    "topic_id": a.get("topic_id"),
                }
                for a in answers
            ]

    # -------------------------------------------------------------------------
    # Sentence Construction
    # -------------------------------------------------------------------------

    async def generate_sentence_construction(
        self,
        user_id: int,
        cefr_level: CEFRLevel = CEFRLevel.A1,
    ) -> dict[str, Any]:
        """
        Generate a sentence construction exercise.

        Returns:
            {
                "exercise_id": str,
                "words": [str],  # Shuffled words to arrange
                "hint": str,
                "expected_answer": str
            }
        """
        # Try to use user's vocabulary
        user_words = await self._word_crud.get_multi(user_id=user_id, limit=10)
        vocab_context = ""
        if user_words:
            vocab_context = f"Try to use some of these words the user knows: {', '.join(w.croatian for w in user_words[:5])}"

        grammar_context = await self._get_learnt_grammar_context(user_id)
        user_context = await self._get_user_context(user_id)

        # Build session key for chat context
        session_key = self._build_session_key(user_id, "sentence_construction")

        # System instruction
        system_instruction = f"""You are a Croatian sentence construction exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE sentences each time - never repeat
2. Vary vocabulary, sentence structures, and topics
3. Always respond with ONLY valid JSON (no markdown)
4. Remember all sentences from this conversation to avoid repetition"""

        prompt = f"""Generate a NEW sentence construction exercise (different from any previous ones).

CEFR Level: {cefr_level.value}
{vocab_context}

Create a Croatian sentence, then provide its words in shuffled order for the learner to arrange.

Respond with ONLY valid JSON:
{{
    "words": ["shuffled", "words", "in", "random", "order"],
    "hint": "English translation or context hint",
    "expected_answer": "Correct Croatian sentence with proper word order"
}}"""

        try:
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "words": data.get("words", []),
                "hint": data.get("hint", ""),
                "expected_answer": data.get("expected_answer", ""),
            }
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Sentence construction generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate sentence construction exercise: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    # -------------------------------------------------------------------------
    # Reading Comprehension
    # -------------------------------------------------------------------------

    async def generate_reading_exercise(
        self,
        user_id: int,
        cefr_level: CEFRLevel = CEFRLevel.A1,
    ) -> dict[str, Any]:
        """
        Generate a reading comprehension exercise.

        Returns:
            {
                "exercise_id": str,
                "passage": str,
                "questions": [{"question": str, "expected_answer": str}]
            }
        """
        grammar_context = await self._get_learnt_grammar_context(user_id)
        user_context = await self._get_user_context(user_id)

        # Build session key for chat context
        session_key = self._build_session_key(user_id, "reading")

        # System instruction
        system_instruction = f"""You are a Croatian reading comprehension exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE passages each time - never repeat topics or scenarios
2. Vary subjects: daily life, travel, food, work, hobbies, culture, etc.
3. Always respond with ONLY valid JSON (no markdown)
4. Remember all passages from this conversation to avoid repetition"""

        prompt = f"""Generate a NEW reading comprehension exercise (different topic from any previous ones).

CEFR Level: {cefr_level.value}

Create a passage in Croatian (200-500 characters) followed by 5-10 comprehension questions.
Questions should test understanding of the passage content - facts, details, and inferences.

Respond with ONLY valid JSON:
{{
    "passage": "Croatian text passage (200-500 characters)",
    "questions": [
        {{"question": "Comprehension question in English or Croatian", "expected_answer": "Expected answer"}}
    ]
}}"""

        try:
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "passage": data.get("passage", ""),
                "questions": data.get("questions", []),
            }
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Reading exercise generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate reading exercise: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    # -------------------------------------------------------------------------
    # Situational Dialogue
    # -------------------------------------------------------------------------

    async def generate_dialogue_exercise(
        self,
        user_id: int,
        cefr_level: CEFRLevel = CEFRLevel.A1,
        scenario: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate a situational dialogue exercise.

        Returns:
            {
                "exercise_id": str,
                "scenario": str,
                "dialogue_start": str,
                "user_role": str,
                "ai_role": str,
                "suggested_phrases": [str]
            }
        """
        scenario_prompt = f"Scenario: {scenario}" if scenario else "Choose a common everyday scenario (different from previous ones)"
        grammar_context = await self._get_learnt_grammar_context(user_id)
        user_context = await self._get_user_context(user_id)

        # Build session key for chat context
        session_key = self._build_session_key(user_id, "dialogue")

        # System instruction
        system_instruction = f"""You are a Croatian dialogue/role-play exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE scenarios each time - never repeat
2. Vary settings: restaurant, shop, hotel, doctor, airport, market, etc.
3. Always respond with ONLY valid JSON (no markdown)
4. Remember all scenarios from this conversation to avoid repetition"""

        prompt = f"""Generate a NEW situational dialogue exercise (different scenario from any previous ones).

CEFR Level: {cefr_level.value}
{scenario_prompt}

Create a role-play scenario where the learner practices real-world Croatian conversation.

Respond with ONLY valid JSON:
{{
    "scenario": "Description of the situation (e.g., 'Ordering food at a restaurant')",
    "dialogue_start": "The opening line of dialogue in Croatian (AI speaks first)",
    "user_role": "The role the user plays (e.g., 'Customer')",
    "ai_role": "The role the AI plays (e.g., 'Waiter')",
    "suggested_phrases": ["Helpful Croatian phrases the user might need"]
}}"""

        try:
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "scenario": data.get("scenario", ""),
                "dialogue_start": data.get("dialogue_start", ""),
                "user_role": data.get("user_role", ""),
                "ai_role": data.get("ai_role", ""),
                "suggested_phrases": data.get("suggested_phrases", []),
            }
        except GeminiServiceError:
            raise
        except Exception as e:
            logger.error(f"Dialogue exercise generation failed: {e}")
            raise GeminiServiceError(
                message=f"Failed to generate dialogue exercise: {str(e)}",
                details={"error_type": type(e).__name__},
            )

    # -------------------------------------------------------------------------
    # Answer Evaluation
    # -------------------------------------------------------------------------

    async def evaluate_answer(
        self,
        user_id: int,
        exercise_type: ExerciseType,
        user_answer: str,
        expected_answer: str,
        context: str = "",
        topic_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate a user's answer with AI assistance.

        Returns:
            {
                "correct": bool,
                "score": float (0.0-1.0),
                "feedback": str,
                "correct_answer": str | None,
                "error_category": str | None,
                "explanation": str | None
            }
        """
        user_context = await self._get_user_context(user_id)

        prompt = f"""Evaluate this Croatian language exercise answer.

{user_context}

Exercise type: {exercise_type.value}
Expected answer: {expected_answer}
User's answer: {user_answer}
Context: {context if context else "language exercise"}

Consider:
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Grammar accuracy
- Alternative valid phrasings
- Partial credit for mostly correct answers
- The student's current level and learning history

Respond with ONLY valid JSON:
{{
    "correct": true/false,
    "score": 0.0 to 1.0 (partial credit allowed),
    "feedback": "Encouraging, educational feedback tailored to the student's level",
    "error_category": "case_error|gender_agreement|verb_conjugation|word_order|spelling|vocabulary|accent|other|null",
    "explanation": "Brief explanation of any mistakes (or null if correct)"
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            correct = bool(data.get("correct", False))
            score = float(data.get("score", 1.0 if correct else 0.0))
            error_cat = data.get("error_category")

            # Log error if present
            if error_cat and error_cat != "null" and not correct:
                try:
                    category = ErrorCategory(error_cat)
                except ValueError:
                    category = ErrorCategory.OTHER

                await self._log_error(
                    user_id=user_id,
                    category=category,
                    topic_id=topic_id,
                    details=user_answer,
                    correction=expected_answer,
                )

            # Update topic progress if applicable
            if topic_id:
                await self._progress_crud.update_progress(
                    user_id=user_id,
                    topic_id=topic_id,
                    correct=correct,
                )

            return {
                "correct": correct,
                "score": score,
                "feedback": data.get("feedback", ""),
                "correct_answer": expected_answer if not correct else None,
                "error_category": error_cat if error_cat != "null" else None,
                "explanation": data.get("explanation"),
            }
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")
            # Fall back to exact match
            is_correct = expected_answer.lower().strip() == user_answer.lower().strip()
            return {
                "correct": is_correct,
                "score": 1.0 if is_correct else 0.0,
                "feedback": "Correct!" if is_correct else f"Expected: {expected_answer}",
                "correct_answer": None if is_correct else expected_answer,
                "error_category": None,
                "explanation": None,
            }

    async def evaluate_reading_answers(
        self,
        user_id: int,
        passage: str,
        questions_and_answers: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        """
        Evaluate all reading comprehension answers at once.

        Args:
            user_id: User ID
            passage: The reading passage
            questions_and_answers: List of dicts with 'question', 'expected_answer', 'user_answer'

        Returns:
            List of evaluation results for each question
        """
        user_context = await self._get_user_context(user_id)

        # Build Q&A list for the prompt
        qa_text = "\n".join(
            f"{i+1}. Question: {qa['question']}\n"
            f"   Expected: {qa['expected_answer']}\n"
            f"   User answered: {qa['user_answer']}"
            for i, qa in enumerate(questions_and_answers)
        )

        prompt = f"""Evaluate these reading comprehension answers.

{user_context}

PASSAGE:
{passage}

QUESTIONS AND ANSWERS:
{qa_text}

Consider:
- Whether the answer demonstrates understanding of the passage
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Grammar accuracy
- Alternative valid phrasings
- Partial credit for mostly correct answers

Respond with ONLY valid JSON - an array with one evaluation object per question:
[
    {{
        "correct": true/false,
        "score": 0.0 to 1.0,
        "feedback": "Brief, encouraging feedback for this answer"
    }}
]

Return exactly {len(questions_and_answers)} evaluation objects in the same order as the questions."""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            # Ensure we have a list
            if not isinstance(data, list):
                data = [data]

            # Pad or trim to match expected count
            results = []
            for i, qa in enumerate(questions_and_answers):
                if i < len(data):
                    item = data[i]
                    results.append({
                        "correct": bool(item.get("correct", False)),
                        "score": float(item.get("score", 1.0 if item.get("correct") else 0.0)),
                        "feedback": item.get("feedback", ""),
                    })
                else:
                    # Fallback for missing evaluations
                    is_correct = qa["expected_answer"].lower().strip() == qa["user_answer"].lower().strip()
                    results.append({
                        "correct": is_correct,
                        "score": 1.0 if is_correct else 0.0,
                        "feedback": "Correct!" if is_correct else f"Expected: {qa['expected_answer']}",
                    })

            return results
        except Exception as e:
            logger.error(f"Batch reading evaluation failed: {e}")
            # Fall back to exact match for all
            return [
                {
                    "correct": qa["expected_answer"].lower().strip() == qa["user_answer"].lower().strip(),
                    "score": 1.0 if qa["expected_answer"].lower().strip() == qa["user_answer"].lower().strip() else 0.0,
                    "feedback": "Correct!" if qa["expected_answer"].lower().strip() == qa["user_answer"].lower().strip() else f"Expected: {qa['expected_answer']}",
                }
                for qa in questions_and_answers
            ]

    # -------------------------------------------------------------------------
    # Topic Rule Generation
    # -------------------------------------------------------------------------

    async def generate_topic_description(
        self,
        topic_id: int,
    ) -> str | None:
        """Generate a rule description for a grammar topic using Gemini."""
        topic = await self._topic_crud.get(topic_id)
        if not topic:
            return None

        prompt = f"""Create a clear, educational explanation of this Croatian grammar topic.

Topic: {topic.name}
CEFR Level: {topic.cefr_level.value}

Write a comprehensive but accessible explanation in Markdown format that includes:
1. What this grammar concept is
2. When/how it's used
3. Formation rules with examples
4. Common patterns and exceptions
5. Practice tips

Target the explanation at {topic.cefr_level.value} level learners.
Use Croatian examples with English translations."""

        try:
            description = await self._gemini._generate(prompt)
            # Save to database
            await self._topic_crud.set_rule_description(topic_id, description)
            return description
        except Exception as e:
            logger.error(f"Topic description generation failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------

    async def log_exercise_activity(
        self,
        user_id: int,
        exercise_type: ExerciseType,
        duration_minutes: int = 0,
        exercises_completed: int = 1,
    ) -> None:
        """Log exercise activity for progress tracking."""
        today = date.today()

        # Try to find existing log for today
        from sqlalchemy import select

        result = await self._db.execute(
            select(ExerciseLog).where(
                ExerciseLog.user_id == user_id,
                ExerciseLog.date == today,
                ExerciseLog.exercise_type == exercise_type,
            )
        )
        log = result.scalar_one_or_none()

        if log:
            log.duration_minutes += duration_minutes
            log.exercises_completed += exercises_completed
        else:
            log = ExerciseLog(
                user_id=user_id,
                date=today,
                exercise_type=exercise_type,
                duration_minutes=duration_minutes,
                exercises_completed=exercises_completed,
            )
            self._db.add(log)

        await self._db.flush()

    async def get_or_create_session(
        self,
        user_id: int,
        exercise_type: ExerciseType,
    ) -> tuple[Session, bool]:
        """
        Get or create an active session for the given exercise type.

        Returns:
            Tuple of (session, created) where created is True if a new session was started.
        """
        return await self._session_crud.get_or_create_active(user_id, exercise_type)

    async def end_session(
        self,
        user_id: int,
        session_id: int,
        outcome: str | None = None,
    ) -> Session | None:
        """End a session with optional outcome summary."""
        from app.schemas.session import SessionEnd

        session_end = SessionEnd(outcome=outcome)
        return await self._session_crud.end_session(session_id, user_id, session_end)

    async def _log_error(
        self,
        user_id: int,
        category: ErrorCategory,
        topic_id: int | None = None,
        details: str | None = None,
        correction: str | None = None,
    ) -> None:
        """Log an error for pattern analysis."""
        error_log = ErrorLog(
            user_id=user_id,
            date=date.today(),
            error_category=category,
            topic_id=topic_id,
            details=details,
            correction=correction,
        )
        self._db.add(error_log)
        await self._db.flush()
