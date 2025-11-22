# Croatian Language Tutor - Project Plan

**Last Updated: 2025-11-22**

---

## Executive Summary

Build a locally-hosted, AI-powered Croatian language learning application using Gemini as the intelligent tutor. The system tracks learning progress, generates contextual exercises, evaluates responses, and adapts to the learner's level. All services run in Docker containers for easy deployment and isolation.

---

## 1. Requirements Analysis

### 1.1 Functional Requirements

#### Core Learning Features
- **Exercise Generation**: Gemini generates exercises based on current knowledge level
- **Answer Evaluation**: AI evaluates user responses with detailed feedback
- **Progress Tracking**: Track known words, completed topics, exercise history
- **Adaptive Learning**: System recommends what to practice based on weaknesses
- **Topic Management**: Organize learning into topics (grammar, vocabulary themes, etc.)

#### Exercise Types (Initial Set)
1. **Vocabulary**: Word translation (HR↔EN), fill-in-the-blank
2. **Grammar**: Conjugation, declension, sentence construction
3. **Reading**: Short text comprehension
4. **Listening**: (Future phase - text-to-speech integration)

#### Data Tracking
- Words learned (with proficiency score per word)
- Topics completed/in-progress
- Exercise history with scores
- Weak areas identified by Gemini
- Session history

### 1.2 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Deployment | Local Docker containers only |
| Users | Single user, no auth required |
| Data Persistence | PostgreSQL for structured data |
| API Response Time | < 5s for Gemini responses (API-bound) |
| Frontend UX | Modern, minimal configuration styling |
| Offline Mode | Not required (Gemini API dependency) |

### 1.3 Constraints

- **Gemini API**: Requires valid API key, subject to rate limits
- **Local Only**: No cloud deployment considerations
- **Single User**: No multi-tenancy, auth, or user management
- **Budget**: Gemini API costs (free tier available)

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
| Python Version | 3.12+ | Latest stable, performance improvements |
| ORM | SQLAlchemy 2.0 | Async support, mature, well-documented |
| Migrations | Alembic | Standard for SQLAlchemy |
| Gemini Client | google-generativeai | Official SDK |
| Validation | Pydantic v2 | Built into FastAPI, fast |
| HTTP Client | httpx | Async HTTP for external calls |

#### Frontend
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | React 18+ with Vite | Fast dev experience, modern tooling |
| UI Library | **Mantine** | Modern, beautiful out-of-box, great DX |
| Routing | React Router v6 | Standard, well-maintained |
| State/Fetching | TanStack Query | Caching, loading states, mutations |
| Language | TypeScript | Type safety, better IDE support |

**Why Mantine over alternatives:**
- Chakra UI: Mantine has better default aesthetics
- MUI: Mantine is lighter, less boilerplate
- Ant Design: Mantine feels more modern
- Tailwind: Mantine provides components, not just utility classes

#### Database
| Component | Technology | Rationale |
|-----------|------------|-----------|
| Database | PostgreSQL 16 | JSON support, arrays, full-text search potential |
| Why not MySQL | PostgreSQL | Better JSON handling for Gemini responses, arrays for word lists |

#### Infrastructure
| Component | Technology |
|-----------|------------|
| Containerization | Docker + Docker Compose |
| Frontend Dev Server | Vite (proxied to backend) |
| API Documentation | Swagger UI (built into FastAPI) |

### 2.3 Database Schema (Initial Design)

```sql
-- Core vocabulary tracking
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    croatian VARCHAR(255) NOT NULL,
    english VARCHAR(255) NOT NULL,
    part_of_speech VARCHAR(50),  -- noun, verb, adjective, etc.
    topic_id INTEGER REFERENCES topics(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Proficiency per word (spaced repetition foundation)
CREATE TABLE word_progress (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words(id),
    proficiency_score FLOAT DEFAULT 0.0,  -- 0.0 to 1.0
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP,
    next_review_at TIMESTAMP
);

-- Learning topics/categories
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty_level INTEGER DEFAULT 1,  -- 1=beginner, 2=intermediate, 3=advanced
    status VARCHAR(50) DEFAULT 'not_started',  -- not_started, in_progress, completed
    created_at TIMESTAMP DEFAULT NOW()
);

-- Exercise history
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    exercise_type VARCHAR(100) NOT NULL,  -- vocab_translation, grammar_conjugation, etc.
    topic_id INTEGER REFERENCES topics(id),
    prompt TEXT NOT NULL,  -- The exercise question/prompt
    expected_answer TEXT,
    user_answer TEXT,
    is_correct BOOLEAN,
    gemini_feedback TEXT,  -- AI evaluation
    score FLOAT,  -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT NOW()
);

-- Session tracking
CREATE TABLE learning_sessions (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    exercises_completed INTEGER DEFAULT 0,
    average_score FLOAT,
    gemini_summary TEXT  -- AI-generated session summary
);

-- Gemini recommendations cache
CREATE TABLE ai_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_type VARCHAR(100),  -- focus_topic, review_words, exercise_type
    content JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);
```

---

## 3. Gemini Integration Design

### 3.1 Prompt Engineering Strategy

The key to effective Gemini integration is consistent, structured prompting.

#### System Prompt (Base Context)
```
You are a Croatian language tutor. Your student is learning Croatian.

Current student profile:
- Known words: {word_count}
- Current topics: {active_topics}
- Weak areas: {weak_areas}
- Recent exercise scores: {recent_scores}

Your responsibilities:
1. Generate exercises appropriate to the student's level
2. Evaluate answers with detailed, encouraging feedback
3. Identify patterns in mistakes
4. Recommend what to practice next

Always respond in structured JSON format as specified.
```

#### Exercise Generation Request
```python
{
    "action": "generate_exercise",
    "exercise_type": "vocabulary_translation",
    "difficulty": "beginner",
    "topic": "basic_greetings",
    "context": {
        "known_words": ["dobar", "dan", "hvala"],
        "recently_practiced": ["zdravo"],
        "weak_words": ["molim"]
    }
}
```

#### Answer Evaluation Request
```python
{
    "action": "evaluate_answer",
    "exercise": {
        "type": "vocabulary_translation",
        "prompt": "Translate 'Good morning' to Croatian",
        "expected": "Dobro jutro",
        "user_answer": "Dobro jutro"
    },
    "context": {
        "previous_attempts": 0,
        "hints_used": false
    }
}
```

### 3.2 Response Parsing

All Gemini responses should follow structured JSON schemas:

```python
# Exercise Response Schema
class ExerciseResponse(BaseModel):
    exercise_type: str
    prompt: str
    expected_answer: str
    hints: list[str]
    difficulty: int
    topic: str

# Evaluation Response Schema
class EvaluationResponse(BaseModel):
    is_correct: bool
    score: float  # 0.0 to 1.0
    feedback: str
    corrections: list[str]
    grammar_notes: list[str]
    encouragement: str
```

---

## 4. Project Structure

```
croatian-tutor/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── config.py            # Settings management
│   │   ├── database.py          # DB connection
│   │   │
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── word.py
│   │   │   ├── topic.py
│   │   │   ├── exercise.py
│   │   │   └── session.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── word.py
│   │   │   ├── exercise.py
│   │   │   └── gemini.py
│   │   │
│   │   ├── api/                 # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # Main router
│   │   │   ├── words.py
│   │   │   ├── topics.py
│   │   │   ├── exercises.py
│   │   │   └── sessions.py
│   │   │
│   │   ├── services/            # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── gemini_service.py
│   │   │   ├── exercise_service.py
│   │   │   └── progress_service.py
│   │   │
│   │   └── crud/                # Database operations
│   │       ├── __init__.py
│   │       ├── word.py
│   │       ├── topic.py
│   │       └── exercise.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_api/
│       └── test_services/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── vite-env.d.ts
│       │
│       ├── components/          # Reusable components
│       │   ├── Layout/
│       │   ├── Exercise/
│       │   └── Progress/
│       │
│       ├── pages/               # Route pages
│       │   ├── Dashboard.tsx
│       │   ├── Practice.tsx
│       │   ├── Vocabulary.tsx
│       │   ├── Topics.tsx
│       │   └── History.tsx
│       │
│       ├── api/                 # API client
│       │   ├── client.ts
│       │   ├── exercises.ts
│       │   └── words.ts
│       │
│       ├── hooks/               # Custom hooks
│       │   └── useExercise.ts
│       │
│       └── types/               # TypeScript types
│           └── index.ts
│
└── dev/                         # Development docs
    └── active/
        └── croatian-tutor-init/
```

---

## 5. Implementation Phases

### Phase 1: Foundation (MVP Infrastructure)
**Goal**: Running containers with basic connectivity

1. Docker Compose setup with all services
2. FastAPI skeleton with health endpoints
3. PostgreSQL with initial schema
4. React app with Mantine, basic routing
5. Verify frontend ↔ backend ↔ database connectivity

### Phase 2: Core Data Layer
**Goal**: CRUD operations for learning data

1. SQLAlchemy models for all tables
2. Alembic migrations
3. CRUD operations for words, topics
4. API endpoints for data management
5. Frontend pages for viewing/managing vocabulary

### Phase 3: Gemini Integration
**Goal**: AI-powered exercise generation and evaluation

1. Gemini service with prompt templates
2. Exercise generation endpoint
3. Answer evaluation endpoint
4. Response parsing and error handling
5. Frontend exercise UI

### Phase 4: Learning Flow
**Goal**: Complete learning experience

1. Practice session management
2. Progress tracking and scoring
3. Spaced repetition logic (basic)
4. Dashboard with stats
5. AI recommendations display

### Phase 5: Polish
**Goal**: Refined user experience

1. Better error handling and loading states
2. Exercise history and review
3. Topic progression visualization
4. Session summaries
5. Data export/import

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API rate limits | Medium | High | Implement caching, batch requests |
| Gemini response format inconsistency | High | Medium | Robust parsing, fallback prompts |
| Gemini API cost overrun | Low | Medium | Monitor usage, cache responses |
| Database schema changes mid-project | Medium | Medium | Use Alembic properly, plan schema |
| Docker networking issues on Windows | Medium | Low | Use standard network configuration |
| Mantine learning curve | Low | Low | Good documentation available |

---

## 7. Success Metrics

### MVP Success Criteria
- [ ] Can add and view vocabulary words
- [ ] Gemini generates relevant exercises
- [ ] Can submit answers and receive feedback
- [ ] Progress is tracked and persisted
- [ ] UI is usable without CSS tweaking

### Quality Metrics
- Backend API response time < 200ms (excluding Gemini)
- Frontend loads in < 2s
- Zero critical bugs in core learning flow
- Docker compose up brings all services to healthy state

---

## 8. Required Resources

### API Keys Required
- **Gemini API Key**: Get from https://makersuite.google.com/app/apikey

### Development Environment
- Docker Desktop installed
- Node.js 20+ (for local frontend dev if needed)
- Python 3.12+ (for local backend dev if needed)
- VS Code or preferred IDE

### External Documentation
- [Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Mantine Docs](https://mantine.dev/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)

---

## 9. Open Questions / Decisions Needed

1. **Spaced repetition algorithm**: Implement SM-2 or simpler custom logic?
2. **Exercise variety**: Start with how many exercise types?
3. **Seed data**: Pre-populate with common Croatian vocabulary?
4. **Audio**: Plan for text-to-speech in future phases?
5. **Grammar rules**: Store Croatian grammar rules in DB or rely on Gemini knowledge?

---

## Appendix A: Docker Compose Draft

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: croatian
      POSTGRES_PASSWORD: tutor_local
      POSTGRES_DB: croatian_tutor
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U croatian -d croatian_tutor"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://croatian:tutor_local@db:5432/croatian_tutor
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

---

## Appendix B: Initial API Endpoints

```
GET  /health                    # Health check
GET  /api/v1/words              # List all words
POST /api/v1/words              # Add new word
GET  /api/v1/words/{id}         # Get word details
PUT  /api/v1/words/{id}         # Update word
DELETE /api/v1/words/{id}       # Delete word

GET  /api/v1/topics             # List topics
POST /api/v1/topics             # Create topic
PUT  /api/v1/topics/{id}        # Update topic

POST /api/v1/exercises/generate # Generate new exercise
POST /api/v1/exercises/evaluate # Evaluate answer
GET  /api/v1/exercises/history  # Get exercise history

GET  /api/v1/progress           # Get overall progress
GET  /api/v1/progress/words     # Get word-level progress
GET  /api/v1/recommendations    # Get AI recommendations

POST /api/v1/sessions/start     # Start learning session
POST /api/v1/sessions/end       # End session with summary
GET  /api/v1/sessions           # Get session history
```
