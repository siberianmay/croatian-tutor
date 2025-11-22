# Croatian Language Tutor - Implementation Tasks

**Last Updated: 2025-11-22**

---

## Phase 1: Foundation (MVP Infrastructure)
**Goal**: Running containers with basic connectivity

### 1.1 Project Setup
- [ ] Create `.env.example` with required variables (S)
- [ ] Create `docker-compose.yml` with all services (M)
- [ ] Create `.gitignore` with proper exclusions (S)
- [ ] Create project `README.md` with setup instructions (S)

### 1.2 Backend Scaffold
- [ ] Create `backend/Dockerfile` (S)
- [ ] Create `backend/pyproject.toml` with dependencies (S)
- [ ] Create `backend/app/main.py` with FastAPI app (S)
- [ ] Create `backend/app/config.py` with Pydantic Settings (S)
- [ ] Create `backend/app/database.py` with async session (M)
- [ ] Add `/health` endpoint (S)
- [ ] Configure CORS for frontend (S)

### 1.3 Frontend Scaffold
- [ ] Initialize Vite + React + TypeScript project (S)
- [ ] Create `frontend/Dockerfile` (S)
- [ ] Install and configure Mantine (S)
- [ ] Create basic App shell with Mantine AppShell (M)
- [ ] Configure React Router with placeholder pages (S)
- [ ] Create API client with axios (S)
- [ ] Verify frontend can call backend `/health` (S)

### 1.4 Database Setup
- [ ] Verify PostgreSQL container starts correctly (S)
- [ ] Create `alembic.ini` and alembic directory (S)
- [ ] Create initial migration with all tables (M)
- [ ] Verify migration runs on container start (S)

### 1.5 Integration Verification
- [ ] `docker compose up` starts all services (S)
- [ ] Frontend accessible at http://localhost:3000 (S)
- [ ] Backend accessible at http://localhost:8000 (S)
- [ ] Swagger docs accessible at http://localhost:8000/docs (S)
- [ ] Backend connects to database (S)

---

## Phase 2: Core Data Layer
**Goal**: CRUD operations for learning data

### 2.1 SQLAlchemy Models
- [ ] Create `models/base.py` with Base class (S)
- [ ] Create `models/word.py` - Word and WordProgress (M)
- [ ] Create `models/topic.py` - Topic model (S)
- [ ] Create `models/exercise.py` - Exercise model (M)
- [ ] Create `models/session.py` - LearningSession model (S)
- [ ] Generate and run Alembic migration (S)

### 2.2 Pydantic Schemas
- [ ] Create `schemas/word.py` - Word DTOs (S)
- [ ] Create `schemas/topic.py` - Topic DTOs (S)
- [ ] Create `schemas/exercise.py` - Exercise DTOs (M)
- [ ] Create `schemas/common.py` - Pagination, etc. (S)

### 2.3 CRUD Operations
- [ ] Create `crud/base.py` with generic CRUD class (M)
- [ ] Create `crud/word.py` - Word operations (S)
- [ ] Create `crud/topic.py` - Topic operations (S)
- [ ] Create `crud/exercise.py` - Exercise operations (S)

### 2.4 API Endpoints - Words
- [ ] `GET /api/v1/words` - List words with pagination (S)
- [ ] `POST /api/v1/words` - Create word (S)
- [ ] `GET /api/v1/words/{id}` - Get single word (S)
- [ ] `PUT /api/v1/words/{id}` - Update word (S)
- [ ] `DELETE /api/v1/words/{id}` - Delete word (S)

### 2.5 API Endpoints - Topics
- [ ] `GET /api/v1/topics` - List topics (S)
- [ ] `POST /api/v1/topics` - Create topic (S)
- [ ] `PUT /api/v1/topics/{id}` - Update topic (S)
- [ ] `DELETE /api/v1/topics/{id}` - Delete topic (S)

### 2.6 Frontend - Vocabulary Management
- [ ] Create Vocabulary page with word list (M)
- [ ] Create Add Word form/modal (M)
- [ ] Create Edit Word functionality (S)
- [ ] Create Delete Word with confirmation (S)
- [ ] Create Topics page with topic list (M)
- [ ] Create Add/Edit Topic functionality (S)

---

## Phase 3: Gemini Integration
**Goal**: AI-powered exercise generation and evaluation

### 3.1 Gemini Service
- [ ] Create `services/gemini_service.py` (L)
- [ ] Implement connection and auth (S)
- [ ] Create system prompt builder (M)
- [ ] Create exercise generation method (L)
- [ ] Create answer evaluation method (L)
- [ ] Implement response parsing with error handling (M)
- [ ] Add retry logic for failed requests (S)

### 3.2 Exercise Service
- [ ] Create `services/exercise_service.py` (M)
- [ ] Implement exercise generation orchestration (M)
- [ ] Implement answer submission and evaluation (M)
- [ ] Implement progress update after evaluation (M)

### 3.3 API Endpoints - Exercises
- [ ] `POST /api/v1/exercises/generate` - Generate exercise (M)
- [ ] `POST /api/v1/exercises/evaluate` - Evaluate answer (M)
- [ ] `GET /api/v1/exercises/history` - Get history (S)
- [ ] `GET /api/v1/exercises/{id}` - Get exercise details (S)

### 3.4 Frontend - Exercise UI
- [ ] Create Practice page layout (M)
- [ ] Create Exercise Card component (M)
- [ ] Create Answer Input component (S)
- [ ] Create Feedback Display component (M)
- [ ] Implement exercise flow (generate → answer → feedback → next) (L)
- [ ] Add loading states during Gemini calls (S)

---

## Phase 4: Learning Flow
**Goal**: Complete learning experience

### 4.1 Progress Tracking
- [ ] Create `services/progress_service.py` (M)
- [ ] Implement word proficiency updates (M)
- [ ] Implement topic progress calculation (M)
- [ ] `GET /api/v1/progress` - Overall progress (S)
- [ ] `GET /api/v1/progress/words` - Word-level progress (S)

### 4.2 Session Management
- [ ] `POST /api/v1/sessions/start` - Start session (S)
- [ ] `POST /api/v1/sessions/end` - End session with summary (M)
- [ ] `GET /api/v1/sessions` - Session history (S)
- [ ] Track exercises within sessions (S)

### 4.3 AI Recommendations
- [ ] Add recommendations request to Gemini service (M)
- [ ] `GET /api/v1/recommendations` - Get AI recommendations (S)
- [ ] Cache recommendations in database (S)

### 4.4 Frontend - Dashboard
- [ ] Create Dashboard page (M)
- [ ] Display overall progress stats (M)
- [ ] Display recent activity (S)
- [ ] Display AI recommendations (S)
- [ ] Quick-start practice button (S)

### 4.5 Frontend - Progress Views
- [ ] Create Progress page (M)
- [ ] Word proficiency visualization (M)
- [ ] Topic completion visualization (M)
- [ ] Weak areas highlight (S)

---

## Phase 5: Polish
**Goal**: Refined user experience

### 5.1 Error Handling
- [ ] Global error boundary in React (S)
- [ ] Toast notifications for errors (S)
- [ ] Backend exception handlers (S)
- [ ] Gemini fallback for API failures (M)

### 5.2 Loading States
- [ ] Skeleton loaders for lists (S)
- [ ] Loading spinners for actions (S)
- [ ] Optimistic updates where appropriate (M)

### 5.3 History & Review
- [ ] Exercise history page (M)
- [ ] Review incorrect exercises (M)
- [ ] Session summaries display (S)

### 5.4 Data Management
- [ ] Export vocabulary to JSON (S)
- [ ] Import vocabulary from JSON (M)
- [ ] Seed data script for initial vocabulary (S)

### 5.5 UX Improvements
- [ ] Keyboard shortcuts for practice (S)
- [ ] Dark/light mode toggle (S) - Mantine built-in
- [ ] Responsive design verification (S)

---

## Effort Legend

| Size | Estimated Effort |
|------|------------------|
| S | < 30 minutes |
| M | 30 min - 2 hours |
| L | 2 - 4 hours |
| XL | 4+ hours |

---

## Dependencies

```
Phase 1 ──────► Phase 2 ──────► Phase 3 ──────► Phase 4 ──────► Phase 5
   │               │               │               │
   │               │               │               │
   └─ Docker       └─ Models       └─ Gemini       └─ Sessions
   └─ FastAPI      └─ CRUD         └─ Exercises    └─ Progress
   └─ React        └─ Basic UI     └─ Practice UI  └─ Dashboard
```

Within phases:
- Models must exist before CRUD
- CRUD must exist before API endpoints
- API endpoints must exist before frontend features
- Gemini service must exist before exercise generation

---

## Current Status

**Phase**: Not Started
**Next Action**: Begin Phase 1.1 - Project Setup

---

## Quick Start Checklist

When resuming work, check:
1. [ ] Docker Desktop is running
2. [ ] `.env` file exists with `GEMINI_API_KEY`
3. [ ] Run `docker compose up` to start services
4. [ ] Check this task file for next uncompleted item
