# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-22**
**Current Phase**: 6 - Progress & Dashboard (NEXT)

---

## SESSION PROGRESS

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

**Deferred to Phase 6:**
- Context Summary Generators (progress_service.py) - depends on exercise/error logs being populated
- Retry logic for Gemini API - simple addition when needed
- Sentence caching - premature optimization

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

### Backend - New Files
| File | Purpose |
|------|---------|
| `backend/app/crud/word.py` | Word CRUD + SM-2 SRS algorithm |
| `backend/app/crud/grammar_topic.py` | Grammar topic + progress CRUD |
| `backend/app/services/drill_service.py` | Vocabulary drill management |
| `backend/app/services/gemini_service.py` | Gemini API wrapper (gemini-2.0-flash) |
| `backend/app/services/exercise_service.py` | AI exercise generation + evaluation |
| `backend/app/api/words.py` | Word REST endpoints + bulk import |
| `backend/app/api/drills.py` | Drill session endpoints + fill-in-blank |
| `backend/app/api/topics.py` | Grammar topics REST endpoints |
| `backend/app/api/exercises.py` | AI exercise endpoints |
| `backend/app/api/router.py` | API router aggregation |
| `backend/app/schemas/drill.py` | Drill Pydantic schemas |

### Backend - Modified Files
| File | Change |
|------|--------|
| `backend/app/crud/__init__.py` | Export WordCRUD |
| `backend/app/services/__init__.py` | Export DrillService, GeminiService |
| `backend/app/api/__init__.py` | Export api_router |
| `backend/app/schemas/__init__.py` | Export drill schemas |
| `backend/app/main.py` | Include API router |

### Frontend - New Files
| File | Purpose |
|------|---------|
| `frontend/src/pages/VocabularyPage.tsx` | Vocabulary CRUD UI + bulk import modal |
| `frontend/src/pages/exercises/ConversationPage.tsx` | AI tutor chat interface |
| `frontend/src/pages/exercises/GrammarPage.tsx` | Grammar exercise UI |
| `frontend/src/pages/exercises/TranslationPage.tsx` | Translation exercise UI |
| `frontend/src/pages/exercises/SentenceConstructionPage.tsx` | Word arrangement UI |
| `frontend/src/pages/exercises/ReadingPage.tsx` | Reading comprehension UI |
| `frontend/src/pages/exercises/DialoguePage.tsx` | Role-play dialogue UI |
| `frontend/src/services/wordApi.ts` | Word API client |
| `frontend/src/services/drillApi.ts` | Drill API client |
| `frontend/src/services/exerciseApi.ts` | Exercise + Topics API client |

### Frontend - Modified Files
| File | Change |
|------|--------|
| `frontend/src/types/index.ts` | Added exercise, topic, conversation types |
| `frontend/src/pages/PracticePage.tsx` | Full drill UI with flashcards |
| `frontend/src/pages/LearnPage.tsx` | Exercise hub with 6 exercise cards |
| `frontend/src/components/layout/AppLayout.tsx` | Added Vocabulary nav item |
| `frontend/src/App.tsx` | Added all exercise routes |

---

## KEY DECISIONS

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gemini model | gemini-2.0-flash | gemini-1.5-flash returned 404 |
| Single user | Hardcoded user_id=1 | Per design, future-extensible |
| SM-2 intervals | 1 day → 6 days → EF multiplier | Standard Anki-compatible |
| Mastery score | 0-10 based on success rate | Simple, visible progress |
| Fill-in-blank | Generated on-demand | No caching needed yet |
| Context summaries | Deferred to Phase 6 | Needs exercise/error data |

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

---

## NEXT STEPS

### Phase 6: Progress & Dashboard (NEXT)
1. Create `backend/app/services/progress_service.py` with context summaries
2. Progress API endpoints (`/api/v1/progress/*`)
3. Dashboard page with stats visualization
4. Error pattern analysis and weak areas display
5. Recent activity tracking

### Phase 7: Polish
- Error handling improvements
- UX polish
- Mobile responsiveness
- Seed data for grammar topics

---

## RUNNING THE PROJECT

```bash
# Start all services
docker compose up --build

# Access points
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Test bulk import
curl -X POST http://localhost:8000/api/v1/words/bulk-import \
  -H "Content-Type: application/json" \
  -d '{"words": ["sunce", "mjesec", "zvijezda"]}'
```

---

## NOTES

- Gemini API key is configured in `.env` file
- Test words exist in DB: voda, kruh, sunce, mjesec, zvijezda
- Frontend hot-reloads, backend uses uvicorn --reload in Docker
