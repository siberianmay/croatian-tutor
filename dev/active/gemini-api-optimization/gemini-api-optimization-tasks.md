# Gemini API Optimization - Tasks

**Last Updated:** 2025-11-23

## Phase 1: Quick Wins (High Priority)

### 1.1 Fix Fill-in-Blank Batching [S]
- [ ] Add `generate_fill_in_blank_batch(words: list[dict])` to `GeminiService`
  - Input: list of `{croatian, english, cefr_level}`
  - Output: list of `{word_id, sentence, answer, hint}`
- [ ] Create batch prompt template (all words in one request)
- [ ] Update `drills.py:88-132` to use batch method
- [ ] Add validation/fallback for partial failures
- [ ] Test with 5, 10, 20 word batches
- [ ] Verify RPD reduction (10 calls → 1 call)

### 1.2 Translation Batch Generation [M]
- [ ] Design `TranslationBatchResponse` schema
  - List of `{exercise_id, topic_id, source_text, expected_answer}`
- [ ] Add `generate_translation_exercises_batch(count, direction, cefr_level)` to `ExerciseService`
- [ ] Create batch prompt template with topic_id requirement
- [ ] Add endpoint `POST /exercises/translation/batch`
- [ ] Create frontend hook `useTranslationBatch()`
- [ ] Update translation exercise page to consume batch
- [ ] Test variety across batch items
- [ ] Test topic_id accuracy

### 1.3 Translation Batch Evaluation [M]
- [ ] Design `TranslationBatchEvaluateRequest` schema
  - List of `{user_answer, expected_answer, topic_id, context}`
- [ ] Design `TranslationBatchEvaluateResponse` schema
  - List of `{correct, score, feedback, error_category, topic_id}`
- [ ] Add `evaluate_translation_answers_batch()` to `ExerciseService`
- [ ] Add batch topic progress update logic
- [ ] Add endpoint `POST /exercises/translation/batch-evaluate`
- [ ] Frontend: collect all answers, submit batch on completion
- [ ] Test topic progress updates
- [ ] Test error categorization accuracy

---

## Phase 2: Extend to Other Exercise Types

### 2.1 Grammar Exercise Batching [M]
- [ ] Design batch request/response schemas
- [ ] Add `generate_grammar_exercises_batch()` to `ExerciseService`
- [ ] Add `evaluate_grammar_answers_batch()` to `ExerciseService`
- [ ] Add endpoints
- [ ] Update frontend
- [ ] Test topic_id selection (Gemini picks from weak topics)

### 2.2 Sentence Construction Batching [M]
- [ ] Design batch request/response schemas
- [ ] Add `generate_sentence_construction_batch()` to `ExerciseService`
- [ ] Add `evaluate_sentence_construction_batch()` to `ExerciseService`
- [ ] Add endpoints
- [ ] Update frontend

---

## Phase 3: Client-Side Optimization

### 3.1 Simple Answer Checking [M]
- [ ] Add `acceptable_answers: list[str]` to exercise response schemas
- [ ] Update Gemini prompts to return alternative acceptable answers
- [ ] Frontend: implement local string matching
- [ ] Frontend: only call API if no local match AND user wants feedback
- [ ] Add "Get AI feedback" toggle/button

### 3.2 Optional Detailed Feedback [S]
- [ ] Add settings/preference for AI feedback level
- [ ] Simple mode: just correct/incorrect
- [ ] Detailed mode: error categorization, explanation
- [ ] Default to simple mode to save API calls

---

## Phase 4: Advanced (Future)

### 4.1 Pre-generation Cache [L]
- [ ] Design exercise cache table/schema
- [ ] Background task to pre-generate exercises
- [ ] Serve from cache, async replenishment
- [ ] Cache invalidation on user progress change

### 4.2 Smart Batching [M]
- [ ] Adaptive batch sizes based on usage patterns
- [ ] Pre-fetch next batch while user works
- [ ] Predictive exercise type selection

---

## Validation Checklist

After each phase, verify:
- [ ] RPD reduction measured and logged
- [ ] Topic progress still updates correctly
- [ ] Error categorization still works
- [ ] Exercise variety maintained
- [ ] No regression in UX

---

## Effort Key
- **S** = Small (< 2 hours)
- **M** = Medium (2-4 hours)
- **L** = Large (4-8 hours)
- **XL** = Extra Large (> 8 hours)

---

## Progress Summary

| Phase | Status | RPD Savings |
|-------|--------|-------------|
| 1.1 Fill-in-blank | Not Started | ~90% for drills |
| 1.2 Translation Gen | Not Started | ~80% |
| 1.3 Translation Eval | Not Started | ~80% |
| 2.1 Grammar | Not Started | ~80% |
| 2.2 Sentence | Not Started | ~80% |
| 3.1 Client-side | Not Started | Variable |
| 3.2 Optional AI | Not Started | Variable |
