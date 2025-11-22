# Croatian Language Tutor - Implementation Tasks

**Last Updated: 2025-11-22**
**Current Phase**: 6 - Progress & Dashboard (NEXT)

---

## Phase 0: Design
**Status**: COMPLETED

- [x] Define learning modes (AI vs non-AI) (M)
- [x] Design vocabulary system (SRS, drill types) (M)
- [x] Design Gemini context strategy (summaries) (M)
- [x] Design session handling (M)
- [x] Decide on user model (single user with table) (S)
- [x] Finalize database schema (M)

---

## Phase 1: Foundation Verification
**Status**: COMPLETED
**Goal**: Confirm existing infrastructure works

### 1.1 Docker & Connectivity
- [x] Verify `docker compose up` starts all services (S)
- [x] Verify PostgreSQL container accessible (S)
- [x] Verify backend health endpoint: `GET /health` (S)
- [x] Verify frontend loads at http://localhost:3000 (S)
- [x] Verify frontend can call backend API (S)

---

## Phase 2: Database & Models
**Status**: COMPLETED
**Goal**: Implement new schema

### 2.1 SQLAlchemy Models
- [x] Replace `backend/app/models/user.py` with new schema (S)
- [x] Replace `backend/app/models/word.py` with SRS fields (M)
- [x] Create `backend/app/models/grammar_topic.py` (S)
- [x] Create `backend/app/models/topic_progress.py` (S)
- [x] Create `backend/app/models/exercise_log.py` (S)
- [x] Create `backend/app/models/error_log.py` (S)
- [x] Create `backend/app/models/session.py` (S)
- [x] Update `backend/app/models/__init__.py` exports (S)
- [x] Delete old unused models (S)

### 2.2 Enums
- [x] Create `PartOfSpeech` enum (S)
- [x] Create `Gender` enum (S)
- [x] Create `CEFRLevel` enum (S)
- [x] Create `ExerciseType` enum (S)
- [x] Create `ErrorCategory` enum (S)

### 2.3 Database Migration
- [x] Create Alembic migration for new schema (M)
- [x] Test migration runs successfully (S)
- [x] Seed default user (id=1) (S)

### 2.4 Pydantic Schemas
- [x] Update `backend/app/schemas/user.py` (S)
- [x] Create `backend/app/schemas/word.py` (M)
- [x] Create `backend/app/schemas/grammar_topic.py` (S)
- [x] Create `backend/app/schemas/progress.py` (S)
- [x] Create `backend/app/schemas/exercise.py` (M)

---

## Phase 3: Vocabulary System (Non-AI Core)
**Status**: COMPLETED
**Goal**: Working vocabulary drills without Gemini

### 3.1 Word CRUD Service
- [x] Create `backend/app/crud/word.py` (M)
- [x] Implement word CRUD operations (M)
- [x] Implement SRS scheduling logic (SM-2) (L)
- [x] Implement get_due_words query (S)

### 3.2 Word API Endpoints
- [x] `GET /api/v1/words` - List words with pagination/filters (S)
- [x] `POST /api/v1/words` - Create single word (S)
- [x] `GET /api/v1/words/{id}` - Get word (S)
- [x] `PUT /api/v1/words/{id}` - Update word (S)
- [x] `DELETE /api/v1/words/{id}` - Delete word (S)
- [x] `GET /api/v1/words/due` - Get words due for review (S)
- [x] `POST /api/v1/words/{id}/review` - Submit drill result, update SRS (M)

### 3.3 Vocabulary Drill Logic (Backend)
- [x] Create `backend/app/services/drill_service.py` (M)
- [x] Implement CR→EN drill selection (S)
- [x] Implement EN→CR drill selection (S)
- [x] Implement fill-in-blank generation (via Gemini) (M)

### 3.4 Vocabulary UI (Frontend)
- [x] Create Vocabulary list page with word table (M)
- [x] Create Add Word modal/form (M)
- [x] Create Edit Word functionality (S)
- [x] Create Delete Word with confirmation (S)
- [x] Create Drill page with card UI (L)
- [x] Implement drill flow (show card → input → feedback) (M)
- [x] Connect drill results to API (S)

---

## Phase 4: Gemini Integration
**Status**: COMPLETED
**Goal**: AI assessment and exercise generation

### 4.1 Gemini Service Foundation
- [x] Create `backend/app/services/gemini_service.py` (M)
- [x] Implement Gemini API connection (S)
- [x] Create base prompt builder (M)
- [x] Implement response parsing with error handling (M)
- [ ] Add retry logic for failed requests (S) - deferred

### 4.2 Word Assessment
- [x] Implement bulk word assessment endpoint (M)
- [x] `POST /api/v1/words/bulk-import` - Bulk import with Gemini assessment (L)
- [x] Parse Gemini response for CEFR level + ease_factor (M)
- [x] Handle duplicates detection (S)

### 4.3 Context Summary Generators
- [ ] Create `backend/app/services/progress_service.py` (M) - deferred to Phase 6
- [ ] Implement vocabulary stats summary (S) - deferred
- [ ] Implement topic mastery summary (S) - deferred
- [ ] Implement exercise variety summary (S) - deferred
- [ ] Implement error patterns summary (S) - deferred
- [ ] Implement combined context builder for prompts (M) - deferred

### 4.4 Fill-in-Blank Generation
- [x] Implement sentence generation for fill-in-blank drills (M)
- [ ] Cache generated sentences per word (optional) (S) - deferred

---

## Phase 5: AI Exercises
**Status**: COMPLETED
**Goal**: Full AI-powered exercise suite

### 5.1 Exercise Service
- [x] Create `backend/app/services/exercise_service.py` (M)
- [x] Implement exercise generation orchestration (L)
- [x] Implement answer evaluation (L)
- [x] Implement error categorization (M)

### 5.2 Grammar Topics
- [x] `GET /api/v1/topics` - List grammar topics (S)
- [x] `GET /api/v1/topics/{id}` - Get topic with rule_description (S)
- [x] `POST /api/v1/topics/{id}/generate-description` - Gemini generates rule (M)
- [x] `GET /api/v1/topics/progress` - User's topic mastery (S)

### 5.3 Exercise Endpoints
- [x] `POST /api/v1/exercises/conversation` - Free conversation turn (M)
- [x] `POST /api/v1/exercises/grammar` - Grammar exercise (M)
- [x] `POST /api/v1/exercises/sentence-construction` - Build sentence (M)
- [x] `POST /api/v1/exercises/reading` - Reading comprehension (M)
- [x] `POST /api/v1/exercises/dialogue` - Situational dialogue (M)
- [x] `POST /api/v1/exercises/translate` - Sentence translation (M)
- [x] `POST /api/v1/exercises/evaluate` - Evaluate answer (M)

### 5.4 Exercise Logging
- [x] Log exercise activity to `exercise_log` (S)
- [x] Log errors to `error_log` with categorization (M)
- [ ] Create session records (S) - deferred to Phase 6

### 5.5 Exercise UI (Frontend)
- [x] Create Conversation chat interface (L)
- [x] Create Grammar exercise component (M)
- [x] Create Sentence construction UI (M)
- [x] Create Reading comprehension UI (M)
- [x] Create Dialogue/role-play UI (M)
- [x] Create Translation exercise UI (M)
- [x] Add loading states for Gemini calls (S)
- [x] Add error feedback display (S)

---

## Phase 6: Progress & Dashboard
**Status**: BLOCKED by Phase 5
**Goal**: Visibility into learning progress

### 6.1 Progress Endpoints
- [ ] `GET /api/v1/progress/summary` - Overall stats (S)
- [ ] `GET /api/v1/progress/vocabulary` - Vocabulary breakdown (S)
- [ ] `GET /api/v1/progress/topics` - Topic mastery overview (S)
- [ ] `GET /api/v1/progress/activity` - Recent activity (S)
- [ ] `GET /api/v1/progress/errors` - Error patterns (S)

### 6.2 Dashboard UI
- [ ] Create Dashboard page layout (M)
- [ ] Display vocabulary stats chart (M)
- [ ] Display topic progress (M)
- [ ] Display recent activity (S)
- [ ] Display error patterns/weak areas (M)
- [ ] Add "Start Practice" quick actions (S)

---

## Phase 7: Polish
**Status**: BLOCKED by Phase 6
**Goal**: Production-ready UX

### 7.1 Error Handling
- [ ] Global error boundary in React (S)
- [ ] Toast notifications for actions (S)
- [ ] Backend exception handlers (S)
- [ ] Gemini error fallbacks (M)

### 7.2 UX Improvements
- [ ] Skeleton loaders for data fetching (S)
- [ ] Keyboard shortcuts for drills (S)
- [ ] Mobile-responsive adjustments (M)

### 7.3 Data Management
- [ ] Export vocabulary to JSON (S)
- [ ] Grammar topic seed data (M)
- [ ] Sample vocabulary seed data (S)

---

## Effort Legend

| Size | Estimated Effort |
|------|------------------|
| S | < 30 minutes |
| M | 30 min - 2 hours |
| L | 2 - 4 hours |

---

## Quick Resume Checklist

When resuming work:
1. [ ] Read `croatian-tutor-init-context.md` for current state
2. [ ] Check which phase is in progress
3. [ ] Continue from first unchecked task in current phase
4. [ ] Update context file if making significant decisions
