"""Exercise API endpoints for AI-powered language exercises."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_current_language
from app.crud.app_settings import AppSettingsCRUD
from app.database import get_db
from app.models.enums import CEFRLevel, ExerciseType
from app.models.user import User
from app.schemas.exercise import (
    ConversationRequest,
    ConversationResponse,
    ExerciseEvaluationRequest,
    ExerciseEvaluationResponse,
    GrammarExerciseRequest,
    GrammarExerciseResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.gemini_service import get_gemini_service
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["exercises"])


async def get_exercise_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ExerciseService:
    """Dependency for ExerciseService with settings-configured Gemini."""
    gemini = get_gemini_service()

    # Configure Gemini with user's settings
    settings_crud = AppSettingsCRUD(db)
    settings = await settings_crud.get_or_create(current_user.id)
    gemini.set_model(settings.gemini_model)

    return ExerciseService(db, gemini)


# -----------------------------------------------------------------------------
# Request/Response Models for additional endpoints
# -----------------------------------------------------------------------------


class SentenceConstructionResponse(BaseModel):
    """Response for sentence construction exercise."""

    exercise_id: str
    words: list[str]
    hint: str
    # expected_answer not exposed to client


class ReadingExerciseResponse(BaseModel):
    """Response for reading comprehension exercise."""

    exercise_id: str
    passage: str
    questions: list[dict]


class DialogueExerciseRequest(BaseModel):
    """Request for dialogue exercise."""

    cefr_level: CEFRLevel = CEFRLevel.A1
    scenario: str | None = None


class DialogueExerciseResponse(BaseModel):
    """Response for dialogue exercise."""

    exercise_id: str
    scenario: str
    dialogue_start: str
    user_role: str
    ai_role: str
    suggested_phrases: list[str]


class DialogueTurnRequest(BaseModel):
    """Request for a dialogue turn."""

    exercise_id: str
    user_message: str
    ai_role: str
    scenario: str
    history: list[dict] = []


class SentenceConstructionRequest(BaseModel):
    """Request for sentence construction exercise."""

    cefr_level: CEFRLevel = CEFRLevel.A1


# -----------------------------------------------------------------------------
# Batch Exercise Models
# -----------------------------------------------------------------------------


class TranslationBatchRequest(BaseModel):
    """Request for batch translation exercises."""

    direction: str = Field(..., pattern="^(cr_en|en_cr)$")
    cefr_level: CEFRLevel = CEFRLevel.A1
    count: int | None = Field(default=None, ge=1, le=20, description="Uses settings default if not provided")


class TranslationBatchItem(BaseModel):
    """Single translation exercise in a batch."""

    exercise_id: str
    topic_id: int | None
    topic_name: str | None
    source_text: str
    source_language: str
    target_language: str
    expected_answer: str


class TranslationBatchResponse(BaseModel):
    """Response with batch of translation exercises."""

    exercises: list[TranslationBatchItem]
    direction: str
    cefr_level: CEFRLevel


class TranslationAnswerItem(BaseModel):
    """Single answer to evaluate in batch."""

    user_answer: str
    expected_answer: str
    source_text: str
    topic_id: int | None = None


class TranslationBatchEvaluateRequest(BaseModel):
    """Request to evaluate multiple translation answers."""

    answers: list[TranslationAnswerItem]
    duration_minutes: int = Field(default=0, ge=0)


class TranslationEvaluationResult(BaseModel):
    """Evaluation result for a single translation."""

    correct: bool
    score: float
    feedback: str
    error_category: str | None = None
    topic_id: int | None = None


class TranslationBatchEvaluateResponse(BaseModel):
    """Response with all translation evaluations."""

    results: list[TranslationEvaluationResult]


# Grammar Batch Models
class GrammarBatchRequest(BaseModel):
    """Request for batch grammar exercises."""

    cefr_level: CEFRLevel | None = None
    count: int | None = Field(default=None, ge=1, le=20, description="Uses settings default if not provided")


class GrammarBatchItem(BaseModel):
    """Single grammar exercise in a batch."""

    exercise_id: str
    topic_id: int
    topic_name: str
    instruction: str
    question: str
    hints: list[str] | None
    expected_answer: str


class GrammarBatchResponse(BaseModel):
    """Response with batch of grammar exercises."""

    exercises: list[GrammarBatchItem]


class GrammarAnswerItem(BaseModel):
    """Single answer to evaluate in grammar batch."""

    user_answer: str
    expected_answer: str
    question: str
    topic_id: int


class GrammarBatchEvaluateRequest(BaseModel):
    """Request to evaluate multiple grammar answers."""

    answers: list[GrammarAnswerItem]
    duration_minutes: int = Field(default=0, ge=0)


class GrammarEvaluationResult(BaseModel):
    """Evaluation result for a single grammar answer."""

    correct: bool
    score: float
    feedback: str
    error_category: str | None = None
    topic_id: int | None = None


class GrammarBatchEvaluateResponse(BaseModel):
    """Response with all grammar evaluations."""

    results: list[GrammarEvaluationResult]


class ReadingExerciseRequest(BaseModel):
    """Request for reading exercise."""

    cefr_level: CEFRLevel = CEFRLevel.A1


class ReadingAnswerItem(BaseModel):
    """Single question-answer pair for batch evaluation."""

    question: str
    expected_answer: str
    user_answer: str


class ReadingBatchEvaluateRequest(BaseModel):
    """Request for batch evaluation of reading answers."""

    passage: str
    answers: list[ReadingAnswerItem]
    duration_minutes: int = Field(default=0, ge=0, description="Time spent on reading exercise in minutes")


class ReadingEvaluationResult(BaseModel):
    """Evaluation result for a single reading answer."""

    correct: bool
    score: float
    feedback: str


class ReadingBatchEvaluateResponse(BaseModel):
    """Response with all reading answer evaluations."""

    results: list[ReadingEvaluationResult]


class AnswerCheckRequest(BaseModel):
    """Request to check any exercise answer."""

    exercise_type: ExerciseType
    user_answer: str
    expected_answer: str
    context: str = ""
    topic_id: int | None = None
    duration_minutes: int = Field(default=0, ge=0, description="Time spent on this exercise in minutes")


# -----------------------------------------------------------------------------
# Conversation Endpoints
# -----------------------------------------------------------------------------


@router.post("/conversation", response_model=ConversationResponse)
async def conversation_turn(
    request: ConversationRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    cefr_level: CEFRLevel = CEFRLevel.A1,
) -> ConversationResponse:
    """
    Have a conversation turn with the Croatian tutor.

    Send a message in Croatian or English and receive a response with
    corrections and suggestions.
    """
    history = [{"role": h.role, "content": h.content} for h in request.history]

    result = await service.conversation_turn(
        user_id=current_user.id,
        message=request.message,
        history=history,
        cefr_level=cefr_level,
        language=language,
    )

    # Log activity
    await service.log_exercise_activity(
        user_id=current_user.id,
        exercise_type=ExerciseType.CONVERSATION,
        exercises_completed=1,
        language=language,
    )

    return ConversationResponse(
        response=result["response"],
        corrections=result.get("corrections"),
        new_vocabulary=result.get("new_vocabulary"),
    )


# -----------------------------------------------------------------------------
# Grammar Endpoints
# -----------------------------------------------------------------------------


@router.post("/grammar", response_model=GrammarExerciseResponse)
async def generate_grammar_exercise(
    request: GrammarExerciseRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    cefr_level: CEFRLevel | None = None,
) -> GrammarExerciseResponse:
    """
    Generate a grammar exercise.

    If topic_id is not provided, auto-selects based on user's weak areas.
    """
    result = await service.generate_grammar_exercise(
        user_id=current_user.id,
        topic_id=request.topic_id,
        cefr_level=cefr_level,
        language=language,
    )

    return GrammarExerciseResponse(
        exercise_id=result["exercise_id"],
        topic_id=result["topic_id"],
        topic_name=result["topic_name"],
        instruction=result["instruction"],
        question=result["question"],
        hints=result.get("hints"),
    )


@router.post("/grammar/batch", response_model=GrammarBatchResponse)
async def generate_grammar_exercises_batch(
    request: GrammarBatchRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GrammarBatchResponse:
    """
    Generate multiple grammar exercises in a single API call.

    Returns a list of exercises that can be completed by the user,
    then submitted together for batch evaluation.
    """
    # Use settings default if count not specified
    count = request.count
    if count is None:
        settings_crud = AppSettingsCRUD(db)
        settings = await settings_crud.get_or_create(current_user.id)
        count = settings.GRAMMAR_BATCH_SIZE

    results = await service.generate_grammar_exercises_batch(
        user_id=current_user.id,
        count=count,
        cefr_level=request.cefr_level,
        language=language,
    )

    exercises = [
        GrammarBatchItem(
            exercise_id=r["exercise_id"],
            topic_id=r["topic_id"],
            topic_name=r["topic_name"],
            instruction=r["instruction"],
            question=r["question"],
            hints=r.get("hints"),
            expected_answer=r["expected_answer"],
        )
        for r in results
    ]

    return GrammarBatchResponse(exercises=exercises)


@router.post("/grammar/batch-evaluate", response_model=GrammarBatchEvaluateResponse)
async def evaluate_grammar_batch(
    request: GrammarBatchEvaluateRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> GrammarBatchEvaluateResponse:
    """
    Evaluate multiple grammar answers in a single API call.

    Updates topic progress for each answer.
    """
    answers = [
        {
            "user_answer": a.user_answer,
            "expected_answer": a.expected_answer,
            "question": a.question,
            "topic_id": a.topic_id,
        }
        for a in request.answers
    ]

    results = await service.evaluate_grammar_answers_batch(
        user_id=current_user.id,
        answers=answers,
        language=language,
    )

    await service.log_exercise_activity(
        user_id=current_user.id,
        exercise_type=ExerciseType.GRAMMAR,
        duration_minutes=request.duration_minutes,
        exercises_completed=len(request.answers),
        language=language,
    )

    return GrammarBatchEvaluateResponse(
        results=[
            GrammarEvaluationResult(
                correct=r["correct"],
                score=r["score"],
                feedback=r["feedback"],
                error_category=r.get("error_category"),
                topic_id=r.get("topic_id"),
            )
            for r in results
        ]
    )


# -----------------------------------------------------------------------------
# Translation Endpoints
# -----------------------------------------------------------------------------


@router.post("/translate", response_model=TranslationResponse)
async def generate_translation_exercise(
    request: TranslationRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> TranslationResponse:
    """
    Generate a translation exercise.

    Direction: "cr_en" (Croatian to English) or "en_cr" (English to Croatian)
    """
    cefr = request.cefr_level or CEFRLevel.A1

    result = await service.generate_translation_exercise(
        user_id=current_user.id,
        direction=request.direction,
        cefr_level=cefr,
        recent_sentences=request.recent_sentences,
        language=language,
    )

    return TranslationResponse(
        exercise_id=result["exercise_id"],
        topic_id=result.get("topic_id"),
        topic_name=result.get("topic_name"),
        source_text=result["source_text"],
        source_language=result["source_language"],
        target_language=result["target_language"],
        expected_answer=result["expected_answer"],
    )


@router.post("/translate/batch", response_model=TranslationBatchResponse)
async def generate_translation_exercises_batch(
    request: TranslationBatchRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TranslationBatchResponse:
    """
    Generate multiple translation exercises in a single API call.

    This endpoint batches exercise generation to reduce API calls.
    Returns a list of exercises that can be completed by the user,
    then submitted together for batch evaluation.
    """
    # Use settings default if count not specified
    count = request.count
    if count is None:
        settings_crud = AppSettingsCRUD(db)
        settings = await settings_crud.get_or_create(current_user.id)
        count = settings.translation_batch_size

    results = await service.generate_translation_exercises_batch(
        user_id=current_user.id,
        direction=request.direction,
        count=count,
        cefr_level=request.cefr_level,
        language=language,
    )

    exercises = [
        TranslationBatchItem(
            exercise_id=r["exercise_id"],
            topic_id=r.get("topic_id"),
            topic_name=r.get("topic_name"),
            source_text=r["source_text"],
            source_language=r["source_language"],
            target_language=r["target_language"],
            expected_answer=r["expected_answer"],
        )
        for r in results
    ]

    return TranslationBatchResponse(
        exercises=exercises,
        direction=request.direction,
        cefr_level=request.cefr_level,
    )


@router.post("/translate/batch-evaluate", response_model=TranslationBatchEvaluateResponse)
async def evaluate_translation_batch(
    request: TranslationBatchEvaluateRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> TranslationBatchEvaluateResponse:
    """
    Evaluate multiple translation answers in a single API call.

    Submit all answers from a batch session for evaluation.
    Updates topic progress for each answer with a topic_id.
    """
    # Convert request to service format
    answers = [
        {
            "user_answer": a.user_answer,
            "expected_answer": a.expected_answer,
            "source_text": a.source_text,
            "topic_id": a.topic_id,
        }
        for a in request.answers
    ]

    results = await service.evaluate_translation_answers_batch(
        user_id=current_user.id,
        answers=answers,
        language=language,
    )

    # Log activity (count all as one session)
    await service.log_exercise_activity(
        user_id=current_user.id,
        exercise_type=ExerciseType.TRANSLATION_EN_CR,  # Generic translation type
        duration_minutes=request.duration_minutes,
        exercises_completed=len(request.answers),
        language=language,
    )

    return TranslationBatchEvaluateResponse(
        results=[
            TranslationEvaluationResult(
                correct=r["correct"],
                score=r["score"],
                feedback=r["feedback"],
                error_category=r.get("error_category"),
                topic_id=r.get("topic_id"),
            )
            for r in results
        ]
    )


# -----------------------------------------------------------------------------
# Sentence Construction Endpoints
# -----------------------------------------------------------------------------


@router.post("/sentence-construction", response_model=SentenceConstructionResponse)
async def generate_sentence_construction(
    request: SentenceConstructionRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> SentenceConstructionResponse:
    """
    Generate a sentence construction exercise.

    Returns shuffled words that the user must arrange into a correct sentence.
    """
    result = await service.generate_sentence_construction(
        user_id=current_user.id,
        cefr_level=request.cefr_level,
        language=language,
    )

    return SentenceConstructionResponse(
        exercise_id=result["exercise_id"],
        words=result["words"],
        hint=result["hint"],
    )


# -----------------------------------------------------------------------------
# Reading Comprehension Endpoints
# -----------------------------------------------------------------------------


@router.post("/reading", response_model=ReadingExerciseResponse)
async def generate_reading_exercise(
    request: ReadingExerciseRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReadingExerciseResponse:
    """
    Generate a reading comprehension exercise.

    Returns a passage in Croatian with comprehension questions.
    Passage length is controlled by app settings.
    """
    # Get passage length from settings
    settings_crud = AppSettingsCRUD(db)
    settings = await settings_crud.get_or_create(current_user.id)

    result = await service.generate_reading_exercise(
        user_id=current_user.id,
        cefr_level=request.cefr_level,
        passage_length=settings.reading_passage_length,
        language=language,
    )

    return ReadingExerciseResponse(
        exercise_id=result["exercise_id"],
        passage=result["passage"],
        questions=result["questions"],
    )


@router.post("/reading/evaluate-batch", response_model=ReadingBatchEvaluateResponse)
async def evaluate_reading_answers(
    request: ReadingBatchEvaluateRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> ReadingBatchEvaluateResponse:
    """
    Evaluate all reading comprehension answers at once.

    Sends all question-answer pairs to AI for batch evaluation.
    """
    questions_and_answers = [
        {
            "question": item.question,
            "expected_answer": item.expected_answer,
            "user_answer": item.user_answer,
        }
        for item in request.answers
    ]

    results = await service.evaluate_reading_answers(
        user_id=current_user.id,
        passage=request.passage,
        questions_and_answers=questions_and_answers,
        language=language,
    )

    # Log activity (count all questions as one exercise session)
    await service.log_exercise_activity(
        user_id=current_user.id,
        exercise_type=ExerciseType.READING,
        duration_minutes=request.duration_minutes,
        exercises_completed=1,
        language=language,
    )

    return ReadingBatchEvaluateResponse(
        results=[
            ReadingEvaluationResult(
                correct=r["correct"],
                score=r["score"],
                feedback=r["feedback"],
            )
            for r in results
        ]
    )


# -----------------------------------------------------------------------------
# Dialogue/Role-play Endpoints
# -----------------------------------------------------------------------------


@router.post("/dialogue", response_model=DialogueExerciseResponse)
async def generate_dialogue_exercise(
    request: DialogueExerciseRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> DialogueExerciseResponse:
    """
    Generate a situational dialogue exercise.

    Creates a role-play scenario for practicing real-world Croatian conversation.
    """
    result = await service.generate_dialogue_exercise(
        user_id=current_user.id,
        cefr_level=request.cefr_level,
        scenario=request.scenario,
        language=language,
    )

    return DialogueExerciseResponse(
        exercise_id=result["exercise_id"],
        scenario=result["scenario"],
        dialogue_start=result["dialogue_start"],
        user_role=result["user_role"],
        ai_role=result["ai_role"],
        suggested_phrases=result["suggested_phrases"],
    )


@router.post("/dialogue/turn", response_model=ConversationResponse)
async def dialogue_turn(
    request: DialogueTurnRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
    cefr_level: CEFRLevel = CEFRLevel.A1,
) -> ConversationResponse:
    """
    Continue a dialogue exercise with a new turn.

    Similar to conversation but within a specific role-play context.
    """
    # Add scenario context to history
    context_message = f"[Role-play scenario: {request.scenario}. You are playing: {request.ai_role}]"
    history = [{"role": "system", "content": context_message}]
    history.extend(request.history)

    result = await service.conversation_turn(
        user_id=current_user.id,
        message=request.user_message,
        history=history,
        cefr_level=cefr_level,
        language=language,
    )

    return ConversationResponse(
        response=result["response"],
        corrections=result.get("corrections"),
        new_vocabulary=result.get("new_vocabulary"),
    )


# -----------------------------------------------------------------------------
# Answer Evaluation
# -----------------------------------------------------------------------------


@router.post("/evaluate", response_model=ExerciseEvaluationResponse)
async def evaluate_answer(
    request: AnswerCheckRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    language: Annotated[str, Depends(get_current_language)],
) -> ExerciseEvaluationResponse:
    """
    Evaluate a user's answer for any exercise type.

    Uses AI to assess correctness, provide feedback, and categorize errors.
    """
    result = await service.evaluate_answer(
        user_id=current_user.id,
        exercise_type=request.exercise_type,
        user_answer=request.user_answer,
        expected_answer=request.expected_answer,
        context=request.context,
        topic_id=request.topic_id,
        language=language,
    )

    # Log activity
    await service.log_exercise_activity(
        user_id=current_user.id,
        exercise_type=request.exercise_type,
        duration_minutes=request.duration_minutes,
        exercises_completed=1,
        language=language,
    )

    return ExerciseEvaluationResponse(
        correct=result["correct"],
        score=result["score"],
        feedback=result["feedback"],
        correct_answer=result.get("correct_answer"),
        error_category=result.get("error_category"),
        explanation=result.get("explanation"),
    )


# -----------------------------------------------------------------------------
# Chat Session Management
# -----------------------------------------------------------------------------


class EndSessionRequest(BaseModel):
    """Request to end an exercise chat session."""

    exercise_type: str = Field(
        ...,
        description="Exercise type: translation, grammar, sentence_construction, reading, dialogue",
    )
    variant: str = Field(
        default="",
        description="Optional variant (e.g., 'cr_en' or 'en_cr' for translation)",
    )


class EndSessionResponse(BaseModel):
    """Response from ending a chat session."""

    ended: bool
    message: str


@router.post("/session/end", response_model=EndSessionResponse)
async def end_exercise_session(
    request: EndSessionRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> EndSessionResponse:
    """
    End an exercise chat session.

    Call this when the user navigates away from an exercise page to clear
    the Gemini chat history. This allows fresh exercises on the next visit.
    """
    ended = service.end_exercise_chat_session(
        user_id=current_user.id,
        exercise_type=request.exercise_type,
        variant=request.variant,
    )

    if ended:
        return EndSessionResponse(
            ended=True,
            message=f"Session ended for {request.exercise_type}",
        )
    return EndSessionResponse(
        ended=False,
        message=f"No active session found for {request.exercise_type}",
    )
