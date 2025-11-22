# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-22**
**Current Phase**: 7 - Polish (IN PROGRESS)

---

## SESSION PROGRESS

### 🟡 Phase 7: Polish (IN PROGRESS)

UX improvements implemented this session:

**Practice Page Improvements**:
- Added Enter key hotkey for "Next Word" button (document-level keydown listener)
- Changed default drill mode to "English → Croatian" (more useful for learning)

**Vocabulary Page Improvements**:
- Added sortable table columns (Croatian, English, Type, Level, Mastery)
- Clickable headers with sort direction indicators (chevron icons)
- Client-side sorting with proper CEFR level ordering (A1 < A2 < ... < C2)

**SRS Algorithm Fixes**:
- Fixed mastery score calculation: now experience-weighted (requires ~10 reviews for max score)
  - Old: 1 correct = mastery 10 (broken)
  - New: 1 correct = mastery 1, 5 correct = 5, 10 correct = 10
- Added `correct_streak` field to Word model for proper SM-2 interval tracking
- Wrong answer now resets streak to 0, restarting interval progression
- Interval calculation uses consecutive streak, not total correct count

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

### Backend - Modified Files (Phase 7)
| File | Change |
|------|--------|
| `backend/app/models/word.py` | Added `correct_streak` field for SM-2 tracking |
| `backend/app/crud/word.py` | Fixed mastery calculation (experience-weighted), streak tracking |
| `backend/alembic/versions/6f2fb341c2b4_add_correct_streak_to_word.py` | Migration for correct_streak |

### Frontend - Modified Files (Phase 7)
| File | Change |
|------|--------|
| `frontend/src/pages/PracticePage.tsx` | Enter hotkey, default mode changed to EN→CR |
| `frontend/src/pages/VocabularyPage.tsx` | Sortable table columns with direction indicators |

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

---

## NEXT STEPS

### Phase 7: Polish (Remaining)
- [ ] Global error boundary in React
- [ ] Toast notifications for actions
- [ ] Skeleton loaders for data fetching
- [ ] Mobile-responsive adjustments
- [ ] Export vocabulary to JSON
- [ ] Grammar topic seed data

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
