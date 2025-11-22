"""Exercise service for AI-powered language exercises."""

import logging
import uuid
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.grammar_topic import GrammarTopicCRUD, TopicProgressCRUD
from app.crud.word import WordCRUD
from app.models.enums import CEFRLevel, ErrorCategory, ExerciseType
from app.models.exercise_log import ExerciseLog
from app.models.error_log import ErrorLog
from app.services.gemini_service import GeminiService

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

        prompt = f"""You are a friendly Croatian language tutor. The student is at {cefr_level.value} level.

Conversation so far:
{history_text}

User: {message}

Respond in a helpful, encouraging way. If the user writes in Croatian:
1. Gently correct any grammar or spelling mistakes
2. Provide the natural way to express their thought
3. Introduce new vocabulary when appropriate

If the user writes in English, respond primarily in Croatian with English explanations as needed.

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

        If topic_id is not provided, auto-selects based on user's weak areas.

        Returns:
            {
                "exercise_id": str,
                "topic_id": int,
                "topic_name": str,
                "instruction": str,
                "question": str,
                "hints": [str] | None,
                "expected_answer": str  # stored for evaluation
            }
        """
        # Select topic
        if topic_id:
            topic = await self._topic_crud.get(topic_id)
        else:
            # Auto-select from weak topics or unpracticed
            weak_topics = await self._progress_crud.get_weak_topics(user_id, limit=3)
            if weak_topics:
                topic = await self._topic_crud.get(weak_topics[0].topic_id)
            else:
                unpracticed = await self._progress_crud.get_unpracticed_topics(user_id, limit=1)
                topic = unpracticed[0] if unpracticed else None

        if not topic:
            # Fallback: get any topic at user's level
            topics = await self._topic_crud.get_multi(cefr_level=cefr_level, limit=1)
            topic = topics[0] if topics else None

        if not topic:
            return {
                "exercise_id": "",
                "topic_id": 0,
                "topic_name": "No topics available",
                "instruction": "Please add grammar topics first.",
                "question": "",
                "hints": None,
                "expected_answer": "",
            }

        # Generate exercise via Gemini
        level = cefr_level.value if cefr_level else topic.cefr_level.value
        prompt = f"""Create a grammar exercise for Croatian learners.

Topic: {topic.name}
CEFR Level: {level}
{"Rule Description: " + topic.rule_description if topic.rule_description else ""}

Create an exercise that tests understanding of this grammar topic.

Respond with ONLY valid JSON:
{{
    "instruction": "Clear instruction in English explaining what to do",
    "question": "The exercise question (can include Croatian text to transform/complete)",
    "hints": ["hint1", "hint2"] or null,
    "expected_answer": "The correct answer"
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            exercise_id = str(uuid.uuid4())

            return {
                "exercise_id": exercise_id,
                "topic_id": topic.id,
                "topic_name": topic.name,
                "instruction": data.get("instruction", "Complete the exercise."),
                "question": data.get("question", ""),
                "hints": data.get("hints"),
                "expected_answer": data.get("expected_answer", ""),
            }
        except Exception as e:
            logger.error(f"Grammar exercise generation failed: {e}")
            return {
                "exercise_id": "",
                "topic_id": topic.id,
                "topic_name": topic.name,
                "instruction": "Exercise generation failed. Please try again.",
                "question": "",
                "hints": None,
                "expected_answer": "",
            }

    # -------------------------------------------------------------------------
    # Translation Exercises
    # -------------------------------------------------------------------------

    async def generate_translation_exercise(
        self,
        user_id: int,
        direction: str,  # "cr_en" or "en_cr"
        cefr_level: CEFRLevel = CEFRLevel.A1,
    ) -> dict[str, Any]:
        """
        Generate a translation exercise.

        Returns:
            {
                "exercise_id": str,
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

        prompt = f"""Create a translation exercise for Croatian learners at {cefr_level.value} level.

Direction: {source_lang} → {target_lang}

Create a sentence appropriate for this level that will help practice common vocabulary and grammar.

Respond with ONLY valid JSON:
{{
    "source_text": "The sentence in {source_lang}",
    "expected_answer": "The correct translation in {target_lang}"
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "source_text": data.get("source_text", ""),
                "source_language": source_lang,
                "target_language": target_lang,
                "expected_answer": data.get("expected_answer", ""),
            }
        except Exception as e:
            logger.error(f"Translation exercise generation failed: {e}")
            return {
                "exercise_id": "",
                "source_text": "Translation generation failed.",
                "source_language": source_lang,
                "target_language": target_lang,
                "expected_answer": "",
            }

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
        user_words = await self._word_crud.get_multi(user_id=1, limit=10)
        vocab_context = ""
        if user_words:
            vocab_context = f"Try to use some of these words the user knows: {', '.join(w.croatian for w in user_words[:5])}"

        prompt = f"""Create a sentence construction exercise for Croatian learners at {cefr_level.value} level.

{vocab_context}

Create a Croatian sentence, then provide its words in shuffled order for the learner to arrange.

Respond with ONLY valid JSON:
{{
    "words": ["shuffled", "words", "in", "random", "order"],
    "hint": "English translation or context hint",
    "expected_answer": "Correct Croatian sentence with proper word order"
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "words": data.get("words", []),
                "hint": data.get("hint", ""),
                "expected_answer": data.get("expected_answer", ""),
            }
        except Exception as e:
            logger.error(f"Sentence construction generation failed: {e}")
            return {
                "exercise_id": "",
                "words": [],
                "hint": "Exercise generation failed.",
                "expected_answer": "",
            }

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
        prompt = f"""Create a reading comprehension exercise for Croatian learners at {cefr_level.value} level.

Create a short passage in Croatian (3-5 sentences) appropriate for this level, followed by 2-3 comprehension questions.

Respond with ONLY valid JSON:
{{
    "passage": "Croatian text passage",
    "questions": [
        {{"question": "Comprehension question in English or Croatian", "expected_answer": "Expected answer"}}
    ]
}}"""

        try:
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "passage": data.get("passage", ""),
                "questions": data.get("questions", []),
            }
        except Exception as e:
            logger.error(f"Reading exercise generation failed: {e}")
            return {
                "exercise_id": "",
                "passage": "Exercise generation failed.",
                "questions": [],
            }

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
        scenario_prompt = f"Scenario: {scenario}" if scenario else "Choose a common everyday scenario"

        prompt = f"""Create a situational dialogue exercise for Croatian learners at {cefr_level.value} level.

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
            response_text = await self._gemini._generate(prompt)
            data = self._gemini._parse_json(response_text)

            return {
                "exercise_id": str(uuid.uuid4()),
                "scenario": data.get("scenario", ""),
                "dialogue_start": data.get("dialogue_start", ""),
                "user_role": data.get("user_role", ""),
                "ai_role": data.get("ai_role", ""),
                "suggested_phrases": data.get("suggested_phrases", []),
            }
        except Exception as e:
            logger.error(f"Dialogue exercise generation failed: {e}")
            return {
                "exercise_id": "",
                "scenario": "Exercise generation failed.",
                "dialogue_start": "",
                "user_role": "",
                "ai_role": "",
                "suggested_phrases": [],
            }

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
        prompt = f"""Evaluate this Croatian language exercise answer.

Exercise type: {exercise_type.value}
Expected answer: {expected_answer}
User's answer: {user_answer}
Context: {context if context else "language exercise"}

Consider:
- Spelling (including Croatian diacritics: č, ć, š, ž, đ)
- Grammar accuracy
- Alternative valid phrasings
- Partial credit for mostly correct answers

Respond with ONLY valid JSON:
{{
    "correct": true/false,
    "score": 0.0 to 1.0 (partial credit allowed),
    "feedback": "Encouraging, educational feedback",
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
