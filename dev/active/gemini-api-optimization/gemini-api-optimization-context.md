# Gemini API Optimization - Context

**Last Updated:** 2025-11-23

## Problem Statement

Free tier Gemini API has limited RPD (requests per day) but generous token limits. Current implementation makes many small API calls (one per exercise generation, one per answer evaluation), depleting RPD while barely touching token allocation.

**User Quote:**
> "We make many small api calls (practically, most exercises are single-sentence based, which means that we have to use one call to get this assignment, then the second to check the answer). We could ask Gemini to give an exercise with chunk of exercises, that the user would do. And then submit a chunk of answers and make Gemini to check all of them in one request."

## Key Files

### Backend - Services
| File | Purpose | Relevance |
|------|---------|-----------|
| `backend/app/services/gemini_service.py` | Core Gemini API wrapper | All API calls go through here |
| `backend/app/services/exercise_service.py` | Exercise generation/evaluation | Main target for batching |
| `backend/app/services/drill_service.py` | Vocabulary drills | No direct Gemini calls |

### Backend - API Routes
| File | Purpose | Relevance |
|------|---------|-----------|
| `backend/app/api/exercises.py` | Exercise endpoints | New batch endpoints go here |
| `backend/app/api/drills.py` | Drill endpoints | Fill-in-blank uses Gemini |

### Frontend (affected by batching)
- Exercise components need to handle batch response/state
- Need to collect answers before batch evaluation

## Current API Call Points

### GeminiService Methods
1. `_generate(prompt)` - Single generation, 1024 tokens max
2. `_generate_bulk(prompt)` - Bulk generation, 4096 tokens max
3. `generate_in_chat(session_key, prompt)` - Chat-based generation with history

### ExerciseService Gemini Calls
| Method | Call Type | Batching Status |
|--------|-----------|-----------------|
| `conversation_turn` | `_generate` | N/A (conversational) |
| `generate_grammar_exercise` | `generate_in_chat` | NOT BATCHED |
| `generate_translation_exercise` | `generate_in_chat` | NOT BATCHED |
| `generate_sentence_construction` | `generate_in_chat` | NOT BATCHED |
| `generate_reading_exercise` | `generate_in_chat` | Includes multi-Q (OK) |
| `generate_dialogue_exercise` | `generate_in_chat` | NOT BATCHED |
| `evaluate_answer` | `_generate` | NOT BATCHED |
| `evaluate_reading_answers` | `_generate` | ALREADY BATCHED |
| `generate_topic_description` | `_generate` | One-time (OK) |

### Drills API Direct Calls
| Location | Call | Issue |
|----------|------|-------|
| `drills.py:118` | `gemini.generate_fill_in_blank()` | Called in loop - N calls |

## Critical Constraint: Topic Progress Tracking

The system tracks grammar topic mastery via `TopicProgress`. When exercises are evaluated:
1. `evaluate_answer()` receives `topic_id`
2. Calls `_progress_crud.update_progress(user_id, topic_id, correct)`
3. This updates mastery scores for spaced repetition

**Batching must preserve this:**
- Batch evaluation request must include `topic_id` per exercise
- Batch evaluation response must indicate which topics to update
- Backend must update all `TopicProgress` records after batch evaluation

## Design Decisions

### Decided
1. **Batch size: 5-10 exercises** - Balance between RPD savings and latency
2. **Keep chat sessions for variety** - Chat history prevents repetition
3. **Backend-driven batching** - Don't expose raw Gemini to frontend
4. **Preserve topic tracking** - Non-negotiable requirement

### Open Questions
1. Should batch exercises be stored server-side or sent to client?
   - Server-side: More control, but adds state management
   - Client-side: Simpler, but exercises visible in network tab
2. How to handle partial batch failures?
   - Option A: Fail entire batch, retry
   - Option B: Return successful items, mark failures
3. Should we implement client-side evaluation?
   - Reduces RPD but loses error categorization

## Dependencies

### Technical
- Gemini API JSON mode (already used)
- Pydantic schemas for batch request/response
- React state management for batch consumption

### External
- Gemini free tier limits (RPD unknown exact number)
- Token limits per request (seems generous)

## Session Progress

### Completed
- [x] Analyzed all Gemini API call points
- [x] Identified fill-in-blank as worst offender
- [x] Created comprehensive optimization plan
- [x] Documented current state and proposed changes

### Next Steps
- [ ] Implement fill-in-blank batching (Phase 1.1)
- [ ] Implement translation batching (Phase 1.2-1.3)
- [ ] Measure RPD reduction

## Related Code Snippets

### Current Fill-in-Blank Loop (Problem)
```python
# drills.py:117-122
for word in words:
    result = await gemini.generate_fill_in_blank(
        word=word.croatian,
        english=word.english,
        cefr_level=word.cefr_level.value,
    )
    items.append(...)
```

### Reading Batch Evaluation (Reference)
```python
# exercise_service.py:762-855
async def evaluate_reading_answers(
    self,
    user_id: int,
    passage: str,
    questions_and_answers: list[dict[str, str]],
) -> list[dict[str, Any]]:
    # Single API call evaluates all answers
```

### Translation Generation (To Be Batched)
```python
# exercise_service.py:324-420
async def generate_translation_exercise(...):
    # Currently generates 1 exercise per call
    response_text = await self._gemini.generate_in_chat(...)
```

## Notes

- Chat sessions (`_chat_sessions` dict in GeminiService) help with variety
- Clearing sessions too often may reduce variety
- Consider batch generation WITHIN a chat session for best of both
