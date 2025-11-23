"""Exercise API endpoints for AI-powered language exercises."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.enums import CEFRLevel, ExerciseType
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

# Single-user app: hardcoded user_id per design decision
DEFAULT_USER_ID = 1


def get_exercise_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ExerciseService:
    """Dependency for ExerciseService."""
    return ExerciseService(db, get_gemini_service())


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
    cefr_level: CEFRLevel = CEFRLevel.A1,
) -> ConversationResponse:
    """
    Have a conversation turn with the Croatian tutor.

    Send a message in Croatian or English and receive a response with
    corrections and suggestions.
    """
    history = [{"role": h.role, "content": h.content} for h in request.history]

    result = await service.conversation_turn(
        user_id=DEFAULT_USER_ID,
        message=request.message,
        history=history,
        cefr_level=cefr_level,
    )

    # Log activity
    await service.log_exercise_activity(
        user_id=DEFAULT_USER_ID,
        exercise_type=ExerciseType.CONVERSATION,
        exercises_completed=1,
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
    cefr_level: CEFRLevel | None = None,
) -> GrammarExerciseResponse:
    """
    Generate a grammar exercise.

    If topic_id is not provided, auto-selects based on user's weak areas.
    """
    result = await service.generate_grammar_exercise(
        user_id=DEFAULT_USER_ID,
        topic_id=request.topic_id,
        cefr_level=cefr_level,
    )

    if not result.get("exercise_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate grammar exercise",
        )

    return GrammarExerciseResponse(
        exercise_id=result["exercise_id"],
        topic_id=result["topic_id"],
        topic_name=result["topic_name"],
        instruction=result["instruction"],
        question=result["question"],
        hints=result.get("hints"),
    )


# -----------------------------------------------------------------------------
# Translation Endpoints
# -----------------------------------------------------------------------------


@router.post("/translate", response_model=TranslationResponse)
async def generate_translation_exercise(
    request: TranslationRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
) -> TranslationResponse:
    """
    Generate a translation exercise.

    Direction: "cr_en" (Croatian to English) or "en_cr" (English to Croatian)
    """
    cefr = request.cefr_level or CEFRLevel.A1

    result = await service.generate_translation_exercise(
        user_id=DEFAULT_USER_ID,
        direction=request.direction,
        cefr_level=cefr,
        recent_sentences=request.recent_sentences,
    )

    if not result.get("exercise_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate translation exercise",
        )

    return TranslationResponse(
        exercise_id=result["exercise_id"],
        source_text=result["source_text"],
        source_language=result["source_language"],
        target_language=result["target_language"],
        expected_answer=result["expected_answer"],
    )


# -----------------------------------------------------------------------------
# Sentence Construction Endpoints
# -----------------------------------------------------------------------------


@router.post("/sentence-construction", response_model=SentenceConstructionResponse)
async def generate_sentence_construction(
    request: SentenceConstructionRequest,
    service: Annotated[ExerciseService, Depends(get_exercise_service)],
) -> SentenceConstructionResponse:
    """
    Generate a sentence construction exercise.

    Returns shuffled words that the user must arrange into a correct sentence.
    """
    result = await service.generate_sentence_construction(
        user_id=DEFAULT_USER_ID,
        cefr_level=request.cefr_level,
    )

    if not result.get("exercise_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate sentence construction exercise",
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
) -> ReadingExerciseResponse:
    """
    Generate a reading comprehension exercise.

    Returns a passage in Croatian with comprehension questions.
    """
    result = await service.generate_reading_exercise(
        user_id=DEFAULT_USER_ID,
        cefr_level=request.cefr_level,
    )

    if not result.get("exercise_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate reading exercise",
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
        user_id=DEFAULT_USER_ID,
        passage=request.passage,
        questions_and_answers=questions_and_answers,
    )

    # Log activity (count all questions as one exercise session)
    await service.log_exercise_activity(
        user_id=DEFAULT_USER_ID,
        exercise_type=ExerciseType.READING,
        duration_minutes=request.duration_minutes,
        exercises_completed=1,
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
) -> DialogueExerciseResponse:
    """
    Generate a situational dialogue exercise.

    Creates a role-play scenario for practicing real-world Croatian conversation.
    """
    result = await service.generate_dialogue_exercise(
        user_id=DEFAULT_USER_ID,
        cefr_level=request.cefr_level,
        scenario=request.scenario,
    )

    if not result.get("exercise_id"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate dialogue exercise",
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
        user_id=DEFAULT_USER_ID,
        message=request.user_message,
        history=history,
        cefr_level=cefr_level,
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
) -> ExerciseEvaluationResponse:
    """
    Evaluate a user's answer for any exercise type.

    Uses AI to assess correctness, provide feedback, and categorize errors.
    """
    result = await service.evaluate_answer(
        user_id=DEFAULT_USER_ID,
        exercise_type=request.exercise_type,
        user_answer=request.user_answer,
        expected_answer=request.expected_answer,
        context=request.context,
        topic_id=request.topic_id,
    )

    # Log activity
    await service.log_exercise_activity(
        user_id=DEFAULT_USER_ID,
        exercise_type=request.exercise_type,
        duration_minutes=request.duration_minutes,
        exercises_completed=1,
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
) -> EndSessionResponse:
    """
    End an exercise chat session.

    Call this when the user navigates away from an exercise page to clear
    the Gemini chat history. This allows fresh exercises on the next visit.
    """
    ended = service.end_exercise_chat_session(
        user_id=DEFAULT_USER_ID,
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
