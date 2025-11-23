# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-23**
**Current Phase**: 8 - Deferred Enhancements (COMPLETED)

---

## SESSION PROGRESS

### ✅ Phase 8: Deferred Enhancements (COMPLETED)

**8.1 Session Tracking (COMPLETED)**:
- `backend/app/schemas/session.py` - Pydantic schemas (SessionCreate, SessionEnd, SessionResponse)
- `backend/app/crud/session.py` - CRUD operations (create, get, get_active, get_multi, end_session, get_or_create_active)
- `backend/app/api/sessions.py` - API endpoints (POST /, GET /, GET /active, GET /{id}, POST /{id}/end)
- `backend/app/api/router.py` - Added sessions router
- `backend/app/services/exercise_service.py` - Added session integration methods

**8.2 Gemini Context Integration (COMPLETED)**:
- `backend/app/services/progress_service.py` - Added `build_gemini_context()` method
- `backend/app/services/exercise_service.py` - Integrated context into all exercise prompts:
  - conversation_turn
  - generate_grammar_exercise
  - generate_translation_exercise
  - generate_sentence_construction
  - generate_reading_exercise
  - generate_dialogue_exercise
  - evaluate_answer

### ✅ Phase 7: Polish (COMPLETED)

All polish tasks implemented this session:

**Error Handling**:
- `ErrorBoundary` component (`frontend/src/components/ErrorBoundary.tsx`) - catches React errors with friendly UI
- Toast notifications via `@mantine/notifications` - utility at `frontend/src/utils/notifications.ts`
- Backend exception handlers (`backend/app/exceptions.py` + `main.py` handlers)
- Gemini service retry logic with 3 attempts, exponential backoff, proper exception classes

**Skeleton Loaders**:
- `TableSkeleton`, `StatCardSkeleton`, `CardSkeleton` in `frontend/src/components/skeletons/`
- Applied to VocabularyPage (table) and ProgressPage (stats + cards)

**Mobile Responsiveness**:
- Burger menu in AppLayout for mobile navigation
- Collapsible navbar with `collapsed: { mobile: !opened }`
- `Table.ScrollContainer` for horizontal scrolling on vocabulary table
- Responsive button groups with `wrap="wrap"` and smaller sizes

**Previous Session Improvements**:
- Enter key hotkey for drill navigation
- Sortable vocabulary table columns
- Experience-weighted mastery scoring
- SRS streak tracking with correct_streak field

### ✅ Phase 6: Progress & Dashboard (COMPLETED)

Full progress tracking and dashboard implemented:
- **Progress Service**: `backend/app/services/progress_service.py` - stats aggregation, context summaries
- **Progress API**: `/api/v1/progress/*` - summary, vocabulary, topics, activity, errors, context
- **Dashboard UI**: `frontend/src/pages/ProgressPage.tsx` - comprehensive stats display
  - Summary stat cards (level, streak, words, due, exercises, errors)
  - Vocabulary mastery ring chart with breakdown by level
  - Grammar topic progress bars
  - Activity heatmap (14-day view)
  - Error patterns and weak areas with suggestions
  - Quick action buttons

### ✅ Phase 5: AI Exercises (COMPLETED)

Full AI exercise suite implemented:
- **Exercise Service**: `backend/app/services/exercise_service.py` - orchestration, evaluation, error categorization
- **Grammar Topic CRUD**: `backend/app/crud/grammar_topic.py` - topics and progress tracking
- **Topics API**: `/api/v1/topics/*` - CRUD, progress, AI description generation
- **Exercises API**: `/api/v1/exercises/*` - conversation, grammar, translation, sentence construction, reading, dialogue
- **Exercise Logging**: Automatic logging to `exercise_log` and `error_log` tables
- **Frontend Exercise Hub**: LearnPage with 6 exercise type cards
- **Conversation Page**: Chat interface with AI tutor, corrections display
- **Grammar Page**: Topic-based grammar exercises with hints
- **Translation Page**: CR↔EN translation with direction selection
- **Sentence Construction Page**: Drag-and-drop word arrangement
- **Reading Page**: Passage + comprehension questions
- **Dialogue Page**: Role-play scenarios with AI partner

### ✅ Phase 4: Gemini Integration (COMPLETED)

AI-powered features implemented:
- **Gemini Service**: `backend/app/services/gemini_service.py` with gemini-2.0-flash model
- **Bulk Import**: POST `/api/v1/words/bulk-import` - AI assesses Croatian words (translation, POS, gender, CEFR level)
- **Fill-in-Blank**: POST `/api/v1/drills/fill-in-blank` - AI generates contextual sentences
- **Answer Evaluation**: `evaluate_answer()` method for AI-powered checking
- **Bulk Import UI**: Modal in Vocabulary page for pasting word lists

### ✅ Phase 3: Vocabulary System (COMPLETED)

Full vocabulary system implemented:
- **Word CRUD**: `backend/app/crud/word.py` with SM-2 SRS algorithm
- **Word API**: All endpoints at `/api/v1/words/*` (list, create, get, update, delete, due, review, bulk-import)
- **Drill Service**: `backend/app/services/drill_service.py` for CR→EN and EN→CR drills
- **Drill API**: `/api/v1/drills/*` (start, check, fill-in-blank)
- **Vocabulary UI**: Full CRUD page at `/vocabulary` with table, search, add/edit/delete modals, bulk import
- **Practice UI**: Flashcard drill page at `/practice` with mode selection, progress tracking, SRS updates

### ✅ Phase 2: Database & Models (COMPLETED)

All database models and schemas implemented:
- **Models created**: User, Word, GrammarTopic, TopicProgress, ExerciseLog, ErrorLog, Session
- **Enums created**: PartOfSpeech, Gender, CEFRLevel, ExerciseType, ErrorCategory
- **Migration**: `502e2ba3bd52_initial_schema_with_all_models.py` applied
- **Default user**: Seeded with id=1
- **Schemas**: All Pydantic schemas for API I/O

### ✅ Phase 1: Foundation Verification (COMPLETED)

All infrastructure verified working.

### ✅ Design Phase (COMPLETED)

All major design decisions finalized.

---

## FILES MODIFIED THIS SESSION

### Backend - New/Modified Files (Phase 7)
| File | Change |
|------|--------|
| `backend/app/exceptions.py` | **NEW** - Custom exceptions (GeminiServiceError, etc.) |
| `backend/app/main.py` | Added exception handlers for custom + generic exceptions |
| `backend/app/services/gemini_service.py` | Added retry logic (3 attempts), rate limit handling, proper exceptions |
| `backend/app/models/word.py` | Added `correct_streak` field for SM-2 tracking |
| `backend/app/crud/word.py` | Fixed mastery calculation (experience-weighted), streak tracking |

### Frontend - New/Modified Files (Phase 7)
| File | Change |
|------|--------|
| `frontend/src/components/ErrorBoundary.tsx` | **NEW** - Global error boundary with dev details |
| `frontend/src/utils/notifications.ts` | **NEW** - Toast utility (success, error, info, warning) |
| `frontend/src/components/skeletons/` | **NEW** - TableSkeleton, StatCardSkeleton, CardSkeleton |
| `frontend/src/components/layout/AppLayout.tsx` | Added burger menu, collapsible mobile nav |
| `frontend/src/main.tsx` | Added Notifications provider |
| `frontend/src/App.tsx` | Wrapped with ErrorBoundary |
| `frontend/src/pages/VocabularyPage.tsx` | TableSkeleton, Table.ScrollContainer, responsive layout |
| `frontend/src/pages/ProgressPage.tsx` | Skeleton loading state with StatCardSkeleton, CardSkeleton |
| `frontend/package.json` | Added @mantine/notifications |

---

## KEY DECISIONS

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gemini model | gemini-2.0-flash | gemini-1.5-flash returned 404 |
| Single user | Hardcoded user_id=1 | Per design, future-extensible |
| SM-2 intervals | 1 day → 6 days → EF multiplier | Standard Anki-compatible |
| Mastery score | Experience-weighted (reviews/10 factor) | Prevents instant max mastery |
| Fill-in-blank | Generated on-demand | No caching needed yet |
| Mastery threshold | score >= 7 = mastered | Clear boundary for stats |
| Streak calculation | Consecutive days with activity | Standard gamification pattern |
| Level progression | 10 mastered words at level = advance | Simple, motivating |
| SRS streak | Track consecutive correct, reset on wrong | Proper SM-2 interval reset |
| Default drill mode | English → Croatian | More useful for active recall |

---

## API ENDPOINTS IMPLEMENTED

### Words API (`/api/v1/words`)
- `GET /` - List words with pagination/filters
- `GET /count` - Count words
- `GET /due` - Get words due for SRS review
- `GET /due/count` - Count due words
- `POST /` - Create word
- `GET /{id}` - Get word
- `PUT /{id}` - Update word
- `DELETE /{id}` - Delete word
- `POST /{id}/review` - Submit drill result, update SRS
- `POST /bulk-import` - AI-powered bulk import

### Drills API (`/api/v1/drills`)
- `POST /start` - Start drill session (CR→EN or EN→CR)
- `POST /check` - Check drill answer
- `POST /fill-in-blank` - Generate AI fill-in-blank exercises

### Topics API (`/api/v1/topics`)
- `GET /` - List grammar topics
- `GET /count` - Count topics
- `GET /progress` - User's topic progress
- `POST /` - Create topic
- `GET /{id}` - Get topic
- `PUT /{id}` - Update topic
- `DELETE /{id}` - Delete topic
- `POST /{id}/generate-description` - AI generates rule description

### Exercises API (`/api/v1/exercises`)
- `POST /conversation` - Chat with AI tutor
- `POST /grammar` - Generate grammar exercise
- `POST /translate` - Generate translation exercise
- `POST /sentence-construction` - Generate sentence arrangement
- `POST /reading` - Generate reading comprehension
- `POST /dialogue` - Start dialogue scenario
- `POST /dialogue/turn` - Continue dialogue
- `POST /evaluate` - Evaluate any exercise answer

### Progress API (`/api/v1/progress`)
- `GET /summary` - Overall stats (words, streak, level)
- `GET /vocabulary` - Vocabulary breakdown by level/mastery
- `GET /topics` - Grammar topic progress
- `GET /activity` - Recent activity timeline
- `GET /errors` - Error patterns and weak areas
- `GET /context` - Text summary for AI context

### Sessions API (`/api/v1/sessions`)
- `POST /` - Start a new learning session
- `GET /` - List sessions with pagination/filters
- `GET /active` - Get currently active session
- `GET /{id}` - Get specific session
- `POST /{id}/end` - End a session with outcome

### Analytics API (`/api/v1/analytics`)
- `GET /` - Get all analytics (combined)
- `GET /leeches` - Get words with high failure rates
- `GET /forecast` - Get upcoming review forecast by day
- `GET /velocity` - Get learning velocity metrics
- `GET /difficulty` - Get performance breakdown by POS/CEFR level

---

## PROJECT STATUS

**All phases completed.** The croatian-tutor-init task is DONE.

### Summary of Phase 8
- **8.1 Session Tracking** ✅ - Session CRUD, duration/outcome tracking
- **8.2 Gemini Context Integration** ✅ - Context builder for AI prompts
- **8.3 Fill-in-Blank Caching** - SKIPPED (want fresh Gemini evaluation)
- **8.4 Data Export/Import** - SKIPPED (not needed)
- **8.5 Advanced Analytics** ✅ - Leech detection, forecast, velocity, difficulty breakdown

---

## RUNNING THE PROJECT

```bash
# Start all services
docker compose up --build

# Access points
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Test progress endpoint
curl http://localhost:8000/api/v1/progress/summary
```

---

## NOTES

- Gemini API key is configured in `.env` file
- 622 words in DB (bulk imported)
- Frontend hot-reloads, backend uses uvicorn --reload in Docker
- Progress dashboard accessible at /progress
