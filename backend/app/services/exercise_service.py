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

        # Build explicit topic list with mastery scores
        # Scale: 0-1000 (shown as percentage)
        topic_lines = []
        for t in topics_with_mastery:
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

            topic_lines.append(f"'{name}' - {level} ({pct}%)")

        return f"""
USER'S GRAMMAR KNOWLEDGE (use ONLY these patterns, prioritize WEAK topics):
{chr(10).join(topic_lines)}"""

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

        # Get user context for personalized exercise
        grammar_context = await self._get_learnt_grammar_context(user_id)
        user_context = await self._get_user_context(user_id)

        # Build session key for chat context
        session_key = self._build_session_key(user_id, "grammar")

        # System instruction for grammar exercise generation
        system_instruction = f"""You are a Croatian grammar exercise generator.
{user_context}
{grammar_context}

CRITICAL RULES:
1. Generate UNIQUE exercises each time - never repeat the same question or sentence pattern
2. Vary the vocabulary, sentence structures, and scenarios
3. Always respond with ONLY valid JSON (no markdown, no explanation)
4. Track what you've generated in this conversation and avoid repetition"""

        # Generate exercise via Gemini chat session
        level = cefr_level.value if cefr_level else topic.cefr_level.value
        prompt = f"""Generate a NEW grammar exercise (different from any previous ones).

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
            response_text = await self._gemini.generate_in_chat(
                session_key=session_key,
                prompt=prompt,
                system_instruction=system_instruction,
            )
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
        recent_sentences: list[str] | None = None,  # Kept for API compatibility, but chat handles history
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

        grammar_context = await self._get_learnt_grammar_context(user_id)
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
4. Remember all sentences from this conversation to avoid repetition"""

        prompt = f"""Generate a NEW translation exercise (completely different from any previous ones).

Direction: {source_lang} → {target_lang}
CEFR Level: {cefr_level.value}

Create a sentence appropriate for this level that will help practice common vocabulary and grammar.

Respond with ONLY valid JSON:
{{
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

Create a short passage in Croatian (3-5 sentences) followed by 2-3 comprehension questions.

Respond with ONLY valid JSON:
{{
    "passage": "Croatian text passage",
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
