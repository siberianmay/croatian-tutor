# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-22**
**Current Phase**: 4 - Gemini Integration (BLOCKED - need API key)

---

## SESSION PROGRESS

### Phase 3: Vocabulary System (COMPLETED)

Full vocabulary system implemented:
- **Word CRUD**: `backend/app/crud/word.py` with SM-2 SRS algorithm
- **Word API**: All endpoints at `/api/v1/words/*` (list, create, get, update, delete, due, review)
- **Drill Service**: `backend/app/services/drill_service.py` for CR→EN and EN→CR drills
- **Drill API**: `/api/v1/drills/*` (start, check)
- **Vocabulary UI**: Full CRUD page at `/vocabulary` with table, search, add/edit/delete modals
- **Practice UI**: Flashcard drill page at `/practice` with mode selection, progress tracking, SRS updates

### Phase 2: Database & Models (COMPLETED)

All database models and schemas implemented:
- **Models created**: User, Word, GrammarTopic, TopicProgress, ExerciseLog, ErrorLog, Session
- **Enums created**: PartOfSpeech, Gender, CEFRLevel, ExerciseType, ErrorCategory
- **Migration**: `502e2ba3bd52_initial_schema_with_all_models.py` applied
- **Default user**: Seeded with id=1
- **Schemas**: All Pydantic schemas for API I/O

### Phase 1: Foundation Verification (COMPLETED)

All infrastructure verified working:
- Docker Compose: All 3 containers start and run
- PostgreSQL: Accessible and healthy
- Backend: Health endpoint returns `{"status":"healthy"}`
- Frontend: Loads at http://localhost:3000
- Connectivity: Frontend container can reach backend via Docker network
- Swagger Docs: Available at http://localhost:8000/docs

### Design Phase (COMPLETED)

All major design decisions have been finalized:

1. **Dual-Mode Learning**: Algorithmic drills (vocabulary) + AI-powered exercises (Gemini)
2. **Database Schema**: 7 tables with singular names
3. **Gemini Context**: On-demand summaries from raw data
4. **Session Handling**: In-session memory only, metadata storage
5. **User Model**: Single user table with id=1, future-extensible

### What Exists (Pre-Implementation)

**Frontend (Complete Scaffold)**:
- `frontend/package.json` - React 18, Mantine 7, TanStack Query 5, React Router 7
- `frontend/vite.config.ts` - Vite with path aliases
- `frontend/src/main.tsx` - App bootstrap with providers
- `frontend/src/App.tsx` - Routes with lazy loading
- `frontend/src/components/layout/AppLayout.tsx` - Mantine AppShell
- `frontend/src/services/api.ts` - Axios client
- `frontend/src/pages/` - Placeholder pages

**Backend (Scaffold + Old Models)**:
- `backend/app/main.py` - FastAPI app with health endpoint
- `backend/app/config.py` - Pydantic Settings
- `backend/app/database.py` - Async SQLAlchemy setup
- `backend/alembic/` - Migration setup (no migrations run yet)
- `backend/app/models/` - OLD models (need replacement based on new design)

**Infrastructure**:
- `docker-compose.yml` - PostgreSQL, backend, frontend services
- `.env.example` - Environment template

### What Needs To Be Done

1. **Replace backend models** with new schema (singular table names)
2. **Create Alembic migration**
3. **Create Pydantic schemas**
4. **Implement services** (WordService, GeminiService, etc.)
5. **Create API endpoints**
6. **Build frontend features**

---

## KEY DECISIONS

### Made During Design Phase

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Table naming | Singular (user, word, topic) | User preference |
| User model | Keep with id=1 | Future extensibility |
| Gemini memory | Per-session only | Simplicity, summaries sufficient |
| Session storage | Metadata only | No transcript bloat |
| Summary computation | On-demand | Simpler than background jobs |
| SRS algorithm | SM-2 | Proven, Anki-compatible |
| Vocabulary import | Croatian words only → Gemini provides translation + assessment | User workflow preference |
| Phrases | Stored in `word` table with pos='phrase' | Simplicity |
| Fill-in-blank | Generated on-the-fly by Gemini | No storage overhead |
| Grammar topics | Pre-seeded, not dynamic | User control |

### Technical Choices (Confirmed)

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + SQLAlchemy 2.0 (async) |
| Frontend | React 18 + Vite + Mantine 7 |
| Database | PostgreSQL 16 |
| AI | Google Gemini API |
| State | TanStack Query 5 |
| Containers | Docker Compose |

---

## DATABASE SCHEMA REFERENCE

### Tables (7 total)

```
user                 - Single user record, preferences
word                 - Vocabulary with SRS fields
grammar_topic        - Topic definitions + rule descriptions
topic_progress       - User mastery per topic
exercise_log         - Daily activity tracking
error_log            - Categorized mistakes
session              - Exercise session metadata
```

### Key Relationships

```
user (1) ─────────┬────────────── (*) word
                  ├────────────── (*) topic_progress
                  ├────────────── (*) exercise_log
                  ├────────────── (*) error_log
                  └────────────── (*) session

grammar_topic (1) ─┬────────────── (*) topic_progress
                   └────────────── (*) error_log (optional)
```

---

## GEMINI CONTEXT SUMMARIES

### Summary Types

| Summary | Source Table(s) | Refresh |
|---------|-----------------|---------|
| Vocabulary Stats | word | On-demand |
| Topic Mastery | grammar_topic + topic_progress | On-demand |
| Exercise Variety | exercise_log | On-demand (7 days) |
| Error Patterns | error_log | On-demand (14 days) |
| Learning Velocity | Derived from above | On-demand |

### Example Prompt Context

```
[VOCABULARY] 245 words. Strong: 89, Medium: 112, Weak: 44. Due: 23.
[TOPICS] Done: Present Tense (9/10). Learning: Dative (4/10). New: Past Tense.
[ACTIVITY] 7d: Reading 45m, Conversation 30m, Grammar 60m.
[ERRORS] Frequent: case_error (12x). Improving: verb_conjugation.
```

---

## FILES TO MODIFY/CREATE

### Backend - Models (Replace)

| File | Status | Notes |
|------|--------|-------|
| `backend/app/models/user.py` | Replace | New schema |
| `backend/app/models/word.py` | Replace | Add SRS fields |
| `backend/app/models/grammar_topic.py` | Create | New table |
| `backend/app/models/topic_progress.py` | Create | New table |
| `backend/app/models/exercise_log.py` | Create | New table |
| `backend/app/models/error_log.py` | Create | New table |
| `backend/app/models/session.py` | Create | Rename from learning_session |
| `backend/app/models/__init__.py` | Update | Export new models |

### Backend - Schemas (Create)

| File | Status |
|------|--------|
| `backend/app/schemas/user.py` | Update |
| `backend/app/schemas/word.py` | Create |
| `backend/app/schemas/grammar_topic.py` | Create |
| `backend/app/schemas/exercise.py` | Create |
| `backend/app/schemas/progress.py` | Create |

### Backend - Services (Create)

| File | Purpose |
|------|---------|
| `backend/app/services/word_service.py` | CRUD, bulk import, SRS |
| `backend/app/services/gemini_service.py` | API, prompts, parsing |
| `backend/app/services/exercise_service.py` | Generation, evaluation |
| `backend/app/services/progress_service.py` | Stats, summaries |

---

## ENVIRONMENT VARIABLES

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Database (defaults work for local Docker)
DATABASE_URL=postgresql+asyncpg://croatian:tutor_local@db:5432/croatian_tutor
POSTGRES_USER=croatian
POSTGRES_PASSWORD=tutor_local
POSTGRES_DB=croatian_tutor

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## NEXT STEPS

**Phase 4: Gemini Integration** (BLOCKED - need API key)
1. Create `backend/app/services/gemini_service.py`
2. Implement Gemini API connection
3. Build prompt templates for word assessment
4. Implement fill-in-blank sentence generation

**Then:**
5. Phase 5: AI Exercises
6. Phase 6: Progress & Dashboard

---

## NOTES

- Old models in `backend/app/models/` should be replaced, not modified
- Delete unused models: `exercise.py`, `learning_session.py`, `progress.py`, `topic.py`
- Frontend scaffold is complete, just needs feature implementation
