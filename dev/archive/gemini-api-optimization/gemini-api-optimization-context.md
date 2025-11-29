# Gemini API Optimization - Context

**Last Updated:** 2025-11-24

## Problem Statement

Free tier Gemini API has limited RPD (requests per day) but generous token limits. Current implementation makes many small API calls (one per exercise generation, one per answer evaluation), depleting RPD while barely touching token allocation.

**User Quote:**
> "We make many small api calls (practically, most exercises are single-sentence based, which means that we have to use one call to get this assignment, then the second to check the answer). We could ask Gemini to give an exercise with chunk of exercises, that the user would do. And then submit a chunk of answers and make Gemini to check all of them in one request."

## Current Status: Phase 1 + Phase 2.1 Complete ✅

Batching optimizations implemented and working:
- Fill-in-blank exercises now batch all words in 1 API call
- Translation exercises batch 10 exercises per generation call
- Translation evaluation batches all answers in 1 API call
- Grammar exercises batch 10 exercises per generation call
- Grammar evaluation batches all answers in 1 API call
- Expected RPD reduction: ~90% for translation, grammar, and fill-in-blank exercises

## Key Files

### Backend - Services
| File | Purpose | Changes Made |
|------|---------|--------------|
| `backend/app/services/gemini_service.py` | Core Gemini API wrapper | Added `generate_fill_in_blank_batch()`, model randomization |
| `backend/app/services/exercise_service.py` | Exercise generation/evaluation | Added `generate_translation_exercises_batch()`, `evaluate_translation_answers_batch()` |
| `backend/app/services/drill_service.py` | Vocabulary drills | No direct Gemini calls |

### Backend - API Routes
| File | Purpose | Changes Made |
|------|---------|--------------|
| `backend/app/api/exercises.py` | Exercise endpoints | Added batch schemas + 2 new endpoints |
| `backend/app/api/drills.py` | Drill endpoints | Updated to use batch method |

### Frontend
| File | Purpose | Changes Made |
|------|---------|--------------|
| `frontend/src/types/index.ts` | TypeScript types | Added 6 batch-related types |
| `frontend/src/services/exerciseApi.ts` | API client | Added batch methods |
| `frontend/src/pages/exercises/TranslationPage.tsx` | Translation UI | Complete rewrite for batch mode |

## Current API Call Points

### GeminiService Methods
1. `_generate(prompt)` - Single generation, 1024 tokens max
2. `_generate_bulk(prompt)` - Bulk generation, 4096 tokens max
3. `generate_in_chat(session_key, prompt)` - Chat-based generation with history
4. `generate_fill_in_blank_batch(words)` - **NEW** Batch fill-in-blank (Phase 1)

### ExerciseService Gemini Calls
| Method | Call Type | Batching Status |
|--------|-----------|-----------------|
| `conversation_turn` | `_generate` | N/A (conversational) |
| `generate_grammar_exercise` | `generate_in_chat` | Legacy single-exercise |
| `generate_grammar_exercises_batch` | `_generate_bulk` | ✅ **BATCHED (Phase 2.1)** |
| `evaluate_grammar_answers_batch` | `_generate_bulk` | ✅ **BATCHED (Phase 2.1)** |
| `generate_translation_exercise` | `generate_in_chat` | Legacy single-exercise |
| `generate_translation_exercises_batch` | `_generate_bulk` | ✅ **BATCHED (Phase 1)** |
| `evaluate_translation_answers_batch` | `_generate_bulk` | ✅ **BATCHED (Phase 1)** |
| `generate_sentence_construction` | `generate_in_chat` | NOT BATCHED |
| `generate_reading_exercise` | `generate_in_chat` | Includes multi-Q (OK) |
| `generate_dialogue_exercise` | `generate_in_chat` | NOT BATCHED |
| `evaluate_answer` | `_generate` | Legacy single-answer |
| `evaluate_reading_answers` | `_generate` | ALREADY BATCHED |
| `generate_topic_description` | `_generate` | One-time (OK) |

### Drills API
| Location | Call | Status |
|----------|------|--------|
| `drills.py:126` | `gemini.generate_fill_in_blank_batch()` | ✅ **BATCHED (Phase 1)** |

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

### Phase 1 - Completed ✅
- [x] Analyzed all Gemini API call points
- [x] Identified fill-in-blank as worst offender
- [x] Created comprehensive optimization plan
- [x] Documented current state and proposed changes
- [x] Implemented fill-in-blank batching (Phase 1.1)
- [x] Implemented translation batch generation (Phase 1.2)
- [x] Implemented translation batch evaluation (Phase 1.3)
- [x] Updated frontend TranslationPage for batch mode
- [x] All TypeScript and Python syntax checks pass

### Phase 2.1 - Grammar Batching - Completed ✅
- [x] Added `generate_grammar_exercises_batch()` to ExerciseService
- [x] Added `evaluate_grammar_answers_batch()` to ExerciseService
- [x] Added batch endpoints to exercises.py
- [x] Added grammar batch types to frontend
- [x] Rewrote GrammarPage.tsx for batch mode

### Next Steps (Phase 2.2+)
- [ ] Extend batching to sentence construction
- [ ] Add client-side simple evaluation option
- [ ] Measure actual RPD reduction in production

## Related Code Snippets

### Fill-in-Blank Batch (IMPLEMENTED ✅)
```python
# drills.py:115-127 - NOW USES BATCH
batch_input = [
    {"word_id": word.id, "croatian": word.croatian, ...}
    for word in words
]
results = await gemini.generate_fill_in_blank_batch(batch_input)  # 1 API call!
```

### Translation Batch Generation (IMPLEMENTED ✅)
```python
# exercise_service.py:422-524
async def generate_translation_exercises_batch(
    self, user_id: int, direction: str, count: int = 10, cefr_level: CEFRLevel = CEFRLevel.A1
) -> list[dict[str, Any]]:
    # Single API call generates all exercises with topic_ids
    response_text = await self._gemini._generate_bulk(prompt)
```

### Translation Batch Evaluation (IMPLEMENTED ✅)
```python
# exercise_service.py:526-660
async def evaluate_translation_answers_batch(
    self, user_id: int, answers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    # Single API call evaluates all, updates TopicProgress for each
```

### Grammar Batch Generation (IMPLEMENTED ✅)
```python
# exercise_service.py:320-407
async def generate_grammar_exercises_batch(
    self, user_id: int, count: int = 10, cefr_level: CEFRLevel | None = None
) -> list[dict[str, Any]]:
    # Single API call generates all exercises with topic_ids
```

### Grammar Batch Evaluation (IMPLEMENTED ✅)
```python
# exercise_service.py:409-529
async def evaluate_grammar_answers_batch(
    self, user_id: int, answers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    # Single API call evaluates all, updates TopicProgress for each
```

### New API Endpoints
```
POST /exercises/translate/batch          -> TranslationBatchResponse
POST /exercises/translate/batch-evaluate -> TranslationBatchEvaluateResponse
POST /exercises/grammar/batch            -> GrammarBatchResponse
POST /exercises/grammar/batch-evaluate   -> GrammarBatchEvaluateResponse
```

## Notes

- Chat sessions (`_chat_sessions` dict in GeminiService) help with variety
- Batch generation does NOT use chat sessions (stateless) - acceptable tradeoff
- Model selection now randomized across available Gemini models (user modification)
- Legacy single-exercise endpoints still available for backward compatibility
