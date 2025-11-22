# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-22**

---

## SESSION PROGRESS

### Completed This Session (✅)

1. **Frontend Scaffold** - Full React/TypeScript/Vite/Mantine setup
   - `frontend/package.json` - Dependencies (React 18, Mantine 7, TanStack Query 5, React Router 7)
   - `frontend/vite.config.ts` - Vite config with path aliases (@/, ~components, ~features, etc.)
   - `frontend/tsconfig.json` + `tsconfig.node.json` - Strict TypeScript config
   - `frontend/Dockerfile` - Node 20 Alpine container
   - `frontend/index.html` - Entry point
   - `frontend/src/main.tsx` - App bootstrap with providers (Mantine, QueryClient, Router)
   - `frontend/src/App.tsx` - Routes with lazy loading + Suspense
   - `frontend/src/config/theme.ts` - Mantine theme config
   - `frontend/src/components/layout/AppLayout.tsx` - AppShell with navigation
   - `frontend/src/services/api.ts` - Axios client with /api/v1 base
   - `frontend/src/types/index.ts` - TypeScript types (Word, Topic, Exercise, etc.)
   - `frontend/src/pages/` - HomePage, LearnPage, PracticePage, ProgressPage (placeholder)

2. **Backend Models Created** (⚠️ MAY NEED REDESIGN)
   - `backend/app/models/user.py` - User model
   - `backend/app/models/topic.py` - Topic model
   - `backend/app/models/word.py` - Word/vocabulary model
   - `backend/app/models/exercise.py` - Exercise model with ExerciseType enum
   - `backend/app/models/learning_session.py` - LearningSession + ExerciseAttempt
   - `backend/app/models/progress.py` - UserProgress model
   - `backend/app/models/__init__.py` - Exports all models

3. **Backend Schemas Started** (🟡 PARTIAL)
   - `backend/app/schemas/user.py` - User schemas created

### In Progress (🟡)

**CRITICAL: DESIGN TUTORING PROCESS FIRST**

The implementation was stopped because we need to design the tutoring flow BEFORE finalizing:
- Database models
- Pydantic schemas
- API routes
- Gemini integration

### Remaining (⏳)

1. **Design Phase (MUST DO FIRST)**
   - Define tutoring flow: How does user interact with Gemini?
   - Determine what context Gemini needs to function as tutor
   - Decide what to persist vs what to generate on-the-fly
   - Redesign database models based on actual requirements

2. **After Design Approved**
   - Finalize/redesign database models
   - Create Pydantic schemas
   - Create Alembic migration
   - Create Gemini service
   - Create API routes
   - Test with docker-compose up

---

## KEY DECISIONS

### Made This Session

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Stop implementation | Yes | Need to design tutoring flow first |
| Models may change | Yes | Created models without understanding Gemini context needs |

### Pending Decisions (MUST DISCUSS)

1. **Tutoring Flow**
   - Free conversation vs structured lessons?
   - Spaced repetition for vocabulary?
   - Progressive difficulty levels?

2. **Gemini's Role**
   - Correct grammar in real-time?
   - Generate exercises dynamically?
   - Maintain conversation context across sessions?

3. **What Context Does Gemini Need?**
   - User's current vocabulary knowledge?
   - Past mistakes/corrections?
   - Topics already covered?
   - Proficiency level?

4. **What to Persist?**
   - Full conversation history or summaries?
   - Per-word mastery scores?
   - Error patterns?

---

## FILES MODIFIED THIS SESSION

### Created (Frontend)
| File | Purpose |
|------|---------|
| `frontend/package.json` | Dependencies |
| `frontend/vite.config.ts` | Vite + aliases |
| `frontend/tsconfig.json` | TypeScript config |
| `frontend/tsconfig.node.json` | Node TypeScript config |
| `frontend/Dockerfile` | Container definition |
| `frontend/index.html` | HTML entry |
| `frontend/src/main.tsx` | React bootstrap |
| `frontend/src/App.tsx` | Routes + lazy loading |
| `frontend/src/vite-env.d.ts` | Vite types |
| `frontend/src/config/theme.ts` | Mantine theme |
| `frontend/src/components/layout/AppLayout.tsx` | App shell |
| `frontend/src/services/api.ts` | Axios client |
| `frontend/src/types/index.ts` | TypeScript types |
| `frontend/src/pages/HomePage.tsx` | Home page |
| `frontend/src/pages/LearnPage.tsx` | Learn page |
| `frontend/src/pages/PracticePage.tsx` | Practice page |
| `frontend/src/pages/ProgressPage.tsx` | Progress page |

### Created (Backend Models - MAY NEED REDESIGN)
| File | Purpose |
|------|---------|
| `backend/app/models/user.py` | User model |
| `backend/app/models/topic.py` | Topic model |
| `backend/app/models/word.py` | Word model |
| `backend/app/models/exercise.py` | Exercise model |
| `backend/app/models/learning_session.py` | Session + Attempt models |
| `backend/app/models/progress.py` | UserProgress model |
| `backend/app/models/__init__.py` | Model exports |
| `backend/app/schemas/user.py` | User schemas |

### Already Existed (Pre-Session)
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration |
| `.env.example` | Environment template |
| `backend/Dockerfile` | Backend container |
| `backend/pyproject.toml` | Python dependencies |
| `backend/app/main.py` | FastAPI app |
| `backend/app/config.py` | Pydantic Settings |
| `backend/app/database.py` | Async SQLAlchemy setup |
| `backend/alembic/` | Migration setup |

---

## NEXT STEPS

### Immediate (Next Session)

1. **DISCUSS TUTORING DESIGN** with user:
   - How should user interact with tutor?
   - What learning flow makes sense?
   - What does Gemini need to know?

2. After design discussion:
   - Validate/redesign database models
   - Proceed with implementation

### Commands to Run on Resume

```bash
# Start services (to test what exists)
docker compose up --build

# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs
```

---

## Technology Choices (CONFIRMED)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Framework | FastAPI | Async, auto-docs, typing |
| Frontend Framework | React + Vite | Fast dev, modern tooling |
| UI Component Library | Mantine 7 | Beautiful defaults, great DX |
| Database | PostgreSQL | JSON support, arrays, mature |
| ORM | SQLAlchemy 2.0 | Async support |
| AI Service | Gemini API | User requirement |
| Containerization | Docker Compose | Simple local orchestration |
| State Management | TanStack Query | Server state caching |

---

## External Dependencies

### APIs
| Service | Purpose | Documentation |
|---------|---------|---------------|
| Gemini API | AI tutor | https://ai.google.dev/docs |

### Key Libraries (Backend)
- fastapi, sqlalchemy 2.0, alembic, asyncpg, pydantic 2.0, google-generativeai, httpx, uvicorn

### Key Libraries (Frontend)
- react 18, @mantine/core 7, @mantine/hooks, @tanstack/react-query 5, react-router-dom 7, axios, typescript 5

---

## Environment Variables

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

## Risk Notes

| Issue | Status | Notes |
|-------|--------|-------|
| DB models created without design | ⚠️ | May need significant changes after tutoring flow design |
| Schemas partially created | ⚠️ | Only user.py done, stopped before completion |

---

## Notes for Future Development

1. **Audio Support**: Consider ElevenLabs or Google TTS for pronunciation
2. **Spaced Repetition**: SM-2 algorithm for word review scheduling
3. **Export**: Allow exporting vocabulary to Anki format
4. **Backup**: Add DB backup script to docker-compose
