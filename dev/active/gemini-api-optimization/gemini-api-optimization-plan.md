# Gemini API Optimization Plan

**Last Updated:** 2025-11-23

## Executive Summary

The Croatian Tutor application is hitting Gemini API free tier RPD (requests per day) limits while using minimal tokens. This indicates severe request inefficiency - we're making many small API calls instead of batching operations. This plan proposes batching strategies to reduce RPD consumption by 60-80% while maintaining all existing functionality.

## Current State Analysis

### API Call Inventory

| Operation | Current Calls | Location | Notes |
|-----------|---------------|----------|-------|
| **Exercise Generation** | | | |
| Grammar exercise | 1 per exercise | `exercise_service.py:282-288` | Chat-based |
| Translation exercise | 1 per exercise | `exercise_service.py:387-392` | Chat-based |
| Sentence construction | 1 per exercise | `exercise_service.py:480-485` | Chat-based |
| Reading comprehension | 1 per exercise | `exercise_service.py:554-559` | Already includes multiple Qs |
| Dialogue exercise | 1 per exercise | `exercise_service.py:633-638` | Chat-based |
| Fill-in-blank | **N calls for N words** | `drills.py:117-122` | **MAJOR ISSUE** |
| **Answer Evaluation** | | | |
| Single answer eval | 1 per answer | `exercise_service.py:711-712` | Always calls Gemini |
| Reading batch eval | 1 per batch | `exercise_service.py:818-819` | Already optimized |
| **Other** | | | |
| Word assessment | 1 per word | `gemini_service.py:63` | Single word lookup |
| Bulk word assessment | 1 per 10 words | `gemini_service.py:134-136` | Already batched |
| Topic description | 1 per topic | `exercise_service.py:886` | One-time generation |
| Conversation turn | 1 per turn | `exercise_service.py:186` | Required |

### Current Request Flow Per Exercise Type

```
Translation Exercise Session (10 sentences):
├── Generate sentence 1        → 1 API call
├── Evaluate answer 1          → 1 API call
├── Generate sentence 2        → 1 API call
├── Evaluate answer 2          → 1 API call
...
└── Generate + Evaluate 10     → 2 API calls
TOTAL: 20 API calls for 10 sentences
```

```
Fill-in-Blank Session (10 words):
├── Generate exercise 1        → 1 API call
├── Generate exercise 2        → 1 API call
...
└── Generate exercise 10       → 1 API call
└── Evaluate all answers       → 10 API calls (if using AI eval)
TOTAL: 10-20 API calls
```

### Problems Identified

1. **Fill-in-blank N+1 problem** (`drills.py:117-122`)
   - Loop generates 1 exercise per API call
   - 10 words = 10 API calls
   - Easy to batch into 1 call

2. **Generate-then-evaluate pattern**
   - Every exercise requires: 1 generation + 1 evaluation = 2 calls minimum
   - For sentence-level exercises, this adds up fast

3. **No batching for non-reading exercises**
   - Reading already batches evaluation
   - Translation, grammar, sentence construction do not

4. **Always using AI for evaluation**
   - Even simple exact-match checks call Gemini
   - Fallback logic exists but only triggers on errors

## Proposed Future State

### Strategy 1: Batch Exercise Generation

**Concept:** Generate 5-10 exercises in a single API call, store them client-side, serve sequentially.

```
Translation Exercise Session (10 sentences):
├── Generate batch (10 sentences + answers)  → 1 API call
├── User completes all 10                    → 0 API calls (local check)
├── Batch evaluate all answers               → 1 API call
TOTAL: 2 API calls for 10 sentences (90% reduction)
```

**Implementation:**
- New endpoint: `POST /exercises/translation/batch`
- Returns: `{ exercises: [...], expected_answers: [...] }`
- Frontend stores batch, serves one at a time
- New endpoint: `POST /exercises/translation/batch-evaluate`

### Strategy 2: Batch Answer Evaluation

**Concept:** Collect all answers, evaluate in single call (already done for Reading).

**Implementation:**
- Extend `evaluate_reading_answers` pattern to:
  - `evaluate_translation_answers_batch`
  - `evaluate_grammar_answers_batch`
  - `evaluate_sentence_construction_batch`

### Strategy 3: Client-Side Simple Evaluation

**Concept:** Don't call AI for cases where simple string matching suffices.

**When to use client-side:**
- Exact match (case-insensitive, whitespace-normalized)
- Known alternatives list provided in generation response

**When to still use AI:**
- Partial credit scenarios
- Grammar error categorization needed
- Alternative phrasings that aren't pre-known

**Implementation:**
- Generation response includes `acceptable_answers: [...]`
- Frontend checks against list first
- Only call AI if no match AND user wants detailed feedback

### Strategy 4: Fix Fill-in-Blank Batching

**Concept:** Generate all fill-in-blank exercises in one call.

```python
# Current (BAD):
for word in words:
    result = await gemini.generate_fill_in_blank(word)  # N calls

# Proposed (GOOD):
results = await gemini.generate_fill_in_blank_batch(words)  # 1 call
```

### Strategy 5: Topic Progress Tracking with Batch Evaluation

**Critical requirement:** Maintain ability to update `TopicProgress` based on exercise results.

**Solution:** Batch evaluation response includes per-item metadata:
```json
{
  "results": [
    {
      "correct": true,
      "score": 1.0,
      "topic_id": 5,
      "error_category": null
    },
    {
      "correct": false,
      "score": 0.3,
      "topic_id": 12,
      "error_category": "case_error"
    }
  ]
}
```

Backend processes results and updates all `TopicProgress` records in one transaction.

## Implementation Phases

### Phase 1: Quick Wins (Low Risk, High Impact)

**1.1 Fix Fill-in-Blank Batching**
- Add `generate_fill_in_blank_batch()` to `GeminiService`
- Update `drills.py` endpoint to use batch method
- Effort: S | Impact: High (eliminates N calls → 1 call)

**1.2 Add Translation Batch Generation**
- New service method: `generate_translation_exercises_batch()`
- New endpoint: `POST /exercises/translation/batch`
- Effort: M | Impact: High

**1.3 Add Translation Batch Evaluation**
- New service method: `evaluate_translation_answers_batch()`
- New endpoint: `POST /exercises/translation/batch-evaluate`
- Effort: M | Impact: High

### Phase 2: Extend Batching to All Exercise Types

**2.1 Grammar Exercise Batching**
- Batch generation with topic_ids included
- Batch evaluation
- Effort: M | Impact: Medium

**2.2 Sentence Construction Batching**
- Batch generation
- Batch evaluation
- Effort: M | Impact: Medium

### Phase 3: Client-Side Optimization

**3.1 Simple Answer Checking**
- Add `acceptable_answers` field to exercise responses
- Frontend checks locally first
- Only call AI for detailed feedback
- Effort: M | Impact: Medium

**3.2 Optional AI Feedback Toggle**
- Add UI toggle: "Get detailed AI feedback"
- When off, use simple string matching
- Effort: S | Impact: Low-Medium

### Phase 4: Advanced Optimizations (Optional)

**4.1 Pre-generation Cache**
- Background job generates exercises ahead of time
- Store in database/cache
- Serve from cache, replenish async
- Effort: L | Impact: High but complex

**4.2 Exercise Queue System**
- Generate next batch while user works on current
- Zero wait time for user
- Effort: L | Impact: UX improvement

## Detailed Task Breakdown

### Phase 1 Tasks

#### Task 1.1: Fill-in-Blank Batch Generation
- [ ] Add `generate_fill_in_blank_batch(words: list)` to `GeminiService`
- [ ] Create prompt template for batch generation
- [ ] Update `drills.py:88-132` to use batch method
- [ ] Test with 5, 10, 20 word batches
- **Acceptance:** 10 words → 1 API call instead of 10

#### Task 1.2: Translation Batch Generation
- [ ] Add `generate_translation_exercises_batch()` to `ExerciseService`
- [ ] Design response schema with topic_ids
- [ ] Create new endpoint `POST /exercises/translation/batch`
- [ ] Create frontend component to consume batch
- [ ] Test batch sizes: 5, 10
- **Acceptance:** 10 exercises → 1 API call

#### Task 1.3: Translation Batch Evaluation
- [ ] Add `evaluate_translation_answers_batch()` to `ExerciseService`
- [ ] Include topic_id in evaluation request/response
- [ ] Create new endpoint `POST /exercises/translation/batch-evaluate`
- [ ] Update TopicProgress in batch
- [ ] Frontend: collect answers, submit batch
- **Acceptance:** 10 evaluations → 1 API call

### Phase 2 Tasks

#### Task 2.1: Grammar Batch Generation & Evaluation
- [ ] Add `generate_grammar_exercises_batch()`
- [ ] Add `evaluate_grammar_answers_batch()`
- [ ] Create endpoints
- [ ] Update frontend
- **Acceptance:** Same as translation

#### Task 2.2: Sentence Construction Batching
- [ ] Add batch generation method
- [ ] Add batch evaluation method
- [ ] Create endpoints
- [ ] Update frontend
- **Acceptance:** Same as translation

### Phase 3 Tasks

#### Task 3.1: Client-Side Simple Evaluation
- [ ] Add `acceptable_answers` field to all exercise responses
- [ ] Frontend: implement local matching before API call
- [ ] Add "Get detailed feedback" button
- **Acceptance:** Simple matches → 0 API calls

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini inconsistent batch output | Medium | High | Strict JSON schema, validation, fallbacks |
| Topic tracking breaks with batching | Low | High | Include topic_id in all responses, test thoroughly |
| Frontend state complexity | Medium | Medium | Clear state management, useReducer pattern |
| Larger prompts hit token limits | Low | Medium | Monitor token usage, adjust batch sizes |
| Chat history lost with batching | Medium | Low | Maintain separate chat for variety, or accept repetition |

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| API calls per 10 translation exercises | 20 | 2 | Logging |
| API calls per 10 fill-in-blank | 10-20 | 1-2 | Logging |
| API calls per 10 grammar exercises | 20 | 2 | Logging |
| Daily RPD usage | 100%+ (limiting) | <40% | Gemini console |
| Token usage change | Low | +20-50% | Gemini console |

## Trade-offs

### Batching Trade-offs
| Aspect | Pro | Con |
|--------|-----|-----|
| RPD | 60-80% reduction | - |
| Tokens | - | 20-50% increase (acceptable) |
| Latency | Faster after first batch | Longer initial wait |
| Variety | - | May reduce with fixed batches |
| Complexity | - | More frontend state |

### Client-Side Evaluation Trade-offs
| Aspect | Pro | Con |
|--------|-----|-----|
| RPD | Significant reduction | - |
| Feedback quality | - | Less detailed for simple checks |
| Error tracking | - | No AI categorization |
| UX | Faster response | Less intelligent feedback |

## Dependencies

- Backend: Python, FastAPI, Pydantic
- Frontend: React, TypeScript, existing exercise components
- External: Gemini API (no changes needed)

## Recommended Implementation Order

1. **Start with Phase 1.1** (Fill-in-blank fix) - Smallest change, immediate impact
2. **Then Phase 1.2-1.3** (Translation batching) - Most used exercise type
3. **Validate metrics** - Confirm RPD reduction
4. **Phase 2** - Extend to other types
5. **Phase 3** - Only if still hitting limits

## Notes

- Chat session management (`_get_or_create_chat`) helps with variety but contributes to RPD
- Batch generation can still use chat sessions for inter-batch variety
- Consider clearing chat sessions less frequently to reduce setup overhead
