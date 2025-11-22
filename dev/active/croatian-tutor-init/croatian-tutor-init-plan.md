# Croatian Language Tutor - Project Plan

**Last Updated: 2025-11-22**

---

## Executive Summary

Build a locally-hosted, AI-powered Croatian language learning application using Gemini as the intelligent tutor. The system tracks learning progress, generates contextual exercises, evaluates responses, and adapts to the learner's level. All services run in Docker containers for easy deployment and isolation.

---

## ⚠️ CRITICAL: Design-First Approach

**Before implementing features, we MUST design the tutoring experience:**

1. **How does the user interact with the tutor?**
   - Free-form conversation?
   - Structured lessons with exercises?
   - Hybrid approach?

2. **What context does Gemini need to be an effective tutor?**
   - User's vocabulary knowledge?
   - Past mistakes and corrections?
   - Learning history?
   - Current proficiency level?

3. **What should we persist vs generate on-the-fly?**
   - Full conversation history or summaries?
   - Individual word mastery scores?
   - Error patterns?

**The database schema and API design depend entirely on these answers.**

---

## 1. Requirements Analysis

### 1.1 Functional Requirements

#### Core Learning Features
- **AI Tutoring**: Gemini acts as conversational Croatian tutor
- **Exercise Generation**: Context-aware exercises based on learner level
- **Answer Evaluation**: AI evaluates responses with detailed feedback
- **Progress Tracking**: Track vocabulary, topics, exercise history
- **Adaptive Learning**: System recommends what to practice based on weaknesses

#### Exercise Types (Initial Set)
1. **Vocabulary**: Word translation (HR↔EN), fill-in-the-blank
2. **Grammar**: Conjugation, declension, sentence construction
3. **Conversation**: Free-form practice with corrections

### 1.2 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Deployment | Local Docker containers only |
| Users | Single user, no auth required |
| Data Persistence | PostgreSQL for structured data |
| API Response Time | < 5s for Gemini responses (API-bound) |
| Frontend UX | Modern, minimal configuration styling |

### 1.3 Constraints

- **Gemini API**: Requires valid API key, subject to rate limits
- **Local Only**: No cloud deployment
- **Single User**: No multi-tenancy or authentication

---

## 2. Technical Architecture

### 2.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Frontend   │───▶│   Backend    │───▶│  PostgreSQL  │       │
│  │    (React)   │    │   (FastAPI)  │    │   Database   │       │
│  │   Port 3000  │    │   Port 8000  │    │   Port 5432  │       │
│  └──────────────┘    └──────┬───────┘    └──────────────┘       │
│                             │                                    │
│                             ▼                                    │
│                    ┌──────────────┐                             │
│                    │  Gemini API  │                             │
│                    │  (External)  │                             │
│                    └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

#### Backend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | FastAPI | Async, fast, excellent typing, OpenAPI docs |
| Python | 3.12+ | Latest stable |
| ORM | SQLAlchemy 2.0 | Async support |
| Migrations | Alembic | Standard for SQLAlchemy |
| Gemini Client | google-generativeai | Official SDK |
| Validation | Pydantic v2 | Built into FastAPI |

#### Frontend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | React 18 + Vite | Fast dev experience |
| UI Library | Mantine 7 | Modern, beautiful defaults |
| Routing | React Router v7 | Standard |
| State/Fetching | TanStack Query 5 | Caching, loading states |
| Language | TypeScript 5 | Type safety |

#### Database
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Database | PostgreSQL 16 | JSON support, arrays |

---

## 3. Implementation Phases

### Phase 0: Design (MUST COMPLETE FIRST)
**Goal**: Define tutoring experience before building

**Deliverables:**
1. Tutoring flow document answering:
   - User interaction model (conversation vs lessons)
   - Gemini's role and responsibilities
   - Context requirements per request
   - Session/conversation persistence strategy

2. Validated database schema based on requirements

3. API contract design

**Exit Criteria:**
- [ ] Tutoring flow agreed upon
- [ ] Gemini context requirements defined
- [ ] Database schema validated/redesigned
- [ ] Ready to implement

---

### Phase 1: Foundation (MVP Infrastructure)
**Goal**: Running containers with basic connectivity
**Status**: ✅ MOSTLY COMPLETE

**Completed:**
- Docker Compose with PostgreSQL, backend, frontend
- FastAPI skeleton with health endpoint
- React/Vite/Mantine scaffold with routing
- Alembic setup

**Remaining:**
- Verify all services start correctly
- Frontend can call backend
- Database migrations (after Phase 0)

---

### Phase 2: Core Data Layer
**Goal**: CRUD operations for learning data
**Status**: ⏳ BLOCKED by Phase 0

**Depends on Phase 0 design for:**
- Final database schema
- What entities to expose via API
- What progress data to track

---

### Phase 3: Gemini Integration
**Goal**: AI-powered tutoring and exercises
**Status**: ⏳ BLOCKED by Phase 0

**Depends on Phase 0 design for:**
- System prompt structure
- Context to include per request
- Response format expectations
- Conversation vs exercise mode

---

### Phase 4: Learning Flow
**Goal**: Complete learning experience

- Progress tracking
- Session management
- Dashboard with stats

---

### Phase 5: Polish
**Goal**: Refined user experience

- Error handling
- Loading states
- Data export

---

## 4. Phase Dependencies

```
Phase 0 (Design) ──► Phase 1 (Foundation) ──► Phase 2 (Data) ──► Phase 3 (Gemini) ──► Phase 4/5
      │                                            │                   │
      │                                            │                   │
      └─ BLOCKER: Must complete                    └─ Depends on       └─ Depends on
         design before continuing                     schema              context design
```

---

## 5. Open Questions (Phase 0 Must Answer)

### Tutoring Flow
1. **Interaction Model**: Free conversation, structured lessons, or hybrid?
2. **Session Concept**: What defines a "learning session"?
3. **Progression**: Linear topics or adaptive?

### Gemini Context
4. **Per-Request Context**: What does Gemini need to know each time?
5. **Memory**: Should Gemini "remember" past conversations?
6. **Evaluation**: How strict should answer evaluation be?

### Data Persistence
7. **Conversation History**: Store full transcripts or summaries?
8. **Word Mastery**: Track per-word or per-topic proficiency?
9. **Error Tracking**: Record specific mistakes for review?

### Single User Simplification
10. **User Model**: Do we even need a User table for single-user app?
11. **Settings**: Where to store user preferences?

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API rate limits | Medium | High | Cache responses, batch requests |
| Gemini response inconsistency | High | Medium | Robust parsing, fallback prompts |
| Schema changes mid-project | Medium | Medium | Complete Phase 0 design first |
| Over-engineering | Medium | Medium | Start simple, iterate |

---

## 7. Success Metrics

### MVP Success Criteria
- [ ] Can have conversation with AI tutor
- [ ] Gemini generates relevant exercises
- [ ] Can submit answers and receive feedback
- [ ] Progress is tracked and persisted
- [ ] UI is usable without CSS tweaking

---

## 8. Current Status

**Phase**: 0 - Design
**Blocker**: Must define tutoring flow before continuing
**Next Action**: Discuss and document tutoring process

**What Exists:**
- Frontend scaffold (complete)
- Backend skeleton (complete)
- Docker infrastructure (complete)
- Database models (created but need validation)

**What's Blocked:**
- Alembic migration (waiting on schema validation)
- Pydantic schemas (waiting on model validation)
- API routes (waiting on design)
- Gemini integration (waiting on context design)
