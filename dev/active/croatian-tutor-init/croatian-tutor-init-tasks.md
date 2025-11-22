# Croatian Language Tutor - Implementation Tasks

**Last Updated: 2025-11-22**

---

## ⚠️ BLOCKER: Design Tutoring Process First

**Before continuing implementation, we MUST design:**
1. How user interacts with Gemini tutor
2. What context Gemini needs to function effectively
3. What data to persist vs generate on-the-fly
4. Validate/redesign database models based on requirements

---

## Phase 0: Design (NEW - MUST COMPLETE FIRST)
**Goal**: Define tutoring flow before finalizing data models

### 0.1 Tutoring Flow Design
- [ ] Define user interaction model (conversation vs structured lessons) (M)
- [ ] Define Gemini's role and responsibilities (M)
- [ ] Determine what context Gemini needs per request (M)
- [ ] Design conversation/session persistence strategy (M)

### 0.2 Data Model Validation
- [ ] Review created models against tutoring requirements (S)
- [ ] Decide: Do we need User model? (single user app) (S)
- [ ] Define what progress data actually needs tracking (M)
- [ ] Finalize database schema design (M)

---

## Phase 1: Foundation (MVP Infrastructure)
**Goal**: Running containers with basic connectivity

### 1.1 Project Setup
- ✅ Create `.env.example` with required variables
- ✅ Create `docker-compose.yml` with all services
- ✅ Create `.gitignore` with proper exclusions
- ✅ Create project `README.md` with setup instructions

### 1.2 Backend Scaffold
- ✅ Create `backend/Dockerfile`
- ✅ Create `backend/pyproject.toml` with dependencies
- ✅ Create `backend/app/main.py` with FastAPI app
- ✅ Create `backend/app/config.py` with Pydantic Settings
- ✅ Create `backend/app/database.py` with async session
- ✅ Add `/health` endpoint
- ✅ Configure CORS for frontend

### 1.3 Frontend Scaffold
- ✅ Initialize Vite + React + TypeScript project
- ✅ Create `frontend/Dockerfile`
- ✅ Install and configure Mantine
- ✅ Create basic App shell with Mantine AppShell
- ✅ Configure React Router with placeholder pages
- ✅ Create API client with axios
- [ ] Verify frontend can call backend `/health` (S)

### 1.4 Database Setup
- [ ] Verify PostgreSQL container starts correctly (S)
- ✅ Create `alembic.ini` and alembic directory
- [ ] Create initial migration with all tables (M) - BLOCKED by Phase 0
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
**STATUS**: ⏳ BLOCKED by Phase 0 design

### 2.1 SQLAlchemy Models
- 🟡 Create models (CREATED BUT MAY NEED REDESIGN)
  - Created: user.py, topic.py, word.py, exercise.py, learning_session.py, progress.py
  - **NEEDS REVIEW** after tutoring flow design

### 2.2 Pydantic Schemas
- 🟡 Create `schemas/user.py` - User DTOs (PARTIAL - created)
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
**Goal**: AI-powered tutoring and exercises
**STATUS**: ⏳ BLOCKED by Phase 0 design

### 3.1 Gemini Service
- [ ] Create `services/gemini_service.py` (L)
- [ ] Implement connection and auth (S)
- [ ] Create system prompt builder with context (M)
- [ ] Create tutoring conversation method (L)
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
- [ ] `POST /api/v1/chat` - Conversation with tutor (M)
- [ ] `POST /api/v1/exercises/generate` - Generate exercise (M)
- [ ] `POST /api/v1/exercises/evaluate` - Evaluate answer (M)
- [ ] `GET /api/v1/exercises/history` - Get history (S)

### 3.4 Frontend - Tutor UI
- [ ] Create Chat/Conversation component (L)
- [ ] Create Exercise Card component (M)
- [ ] Create Answer Input component (S)
- [ ] Create Feedback Display component (M)
- [ ] Implement exercise flow (M)
- [ ] Add loading states during Gemini calls (S)

---

## Phase 4: Learning Flow
**Goal**: Complete learning experience

### 4.1 Progress Tracking
- [ ] Create `services/progress_service.py` (M)
- [ ] Implement word proficiency updates (M)
- [ ] `GET /api/v1/progress` - Overall progress (S)

### 4.2 Session Management
- [ ] Track learning sessions (M)
- [ ] Session history display (S)

### 4.3 Frontend - Dashboard
- [ ] Create Dashboard page (M)
- [ ] Display progress stats (M)
- [ ] Display recent activity (S)

---

## Phase 5: Polish
**Goal**: Refined user experience

### 5.1 Error Handling
- [ ] Global error boundary in React (S)
- [ ] Toast notifications (S)
- [ ] Backend exception handlers (S)

### 5.2 Loading States
- [ ] Skeleton loaders (S)
- [ ] Loading spinners (S)

### 5.3 Data Management
- [ ] Export vocabulary to JSON (S)
- [ ] Seed data script (S)

---

## Effort Legend

| Size | Estimated Effort |
|------|------------------|
| S | < 30 minutes |
| M | 30 min - 2 hours |
| L | 2 - 4 hours |

---

## Current Status

**Phase**: 0 - Design (NEW)
**Blocker**: Must design tutoring flow before continuing
**Next Action**: Discuss tutoring process with user

---

## Quick Resume Checklist

When resuming work:
1. [ ] Read `croatian-tutor-init-context.md` for session state
2. [ ] Complete Phase 0 design discussion
3. [ ] Review/update database models based on design
4. [ ] Then proceed with Phase 1.5 integration verification
