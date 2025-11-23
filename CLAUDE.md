# Croatian Language Tutor - Claude Code Instructions

## Project Overview

AI-powered Croatian language learning application. Users interact with a Gemini-powered tutor to learn Croatian vocabulary, practice exercises, and track progress.

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL, Alembic
- **Frontend:** React 18, TypeScript, Vite, Mantine UI (planned)
- **AI:** Google Gemini API
- **Infrastructure:** Docker Compose

## Project Structure

```
croatian-tutor/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic + Gemini integration
│   │   └── crud/         # Database operations
│   └── alembic/          # Database migrations
├── frontend/             # React application (to be created)
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── api/
│       └── hooks/
├── dev/                  # Development documentation
│   ├── active/           # Current task docs
│   └── archive/          # Completed task docs
└── docker-compose.yml    # Local development stack
```

## Claude Code Tooling

### Skills (Invoke with Skill tool)

| Skill | Purpose |
|-------|---------|
| `backend-dev-guidelines` | FastAPI patterns, services, CRUD, Pydantic, async |
| `frontend-dev-guidelines` | React patterns, Suspense, TanStack Query, routing |
| `dev-docs` | Task planning, context preservation, documentation |
| `skill-developer` | Creating/modifying Claude skills |

> **⚠️ MANDATORY SKILL USAGE**
>
> **Backend work:** You MUST invoke `Skill(backend-dev-guidelines)` BEFORE writing or modifying ANY backend code (routes, services, CRUD, models, schemas, migrations, tests).
>
> **Frontend work:** You MUST invoke `Skill(frontend-dev-guidelines)` BEFORE writing or modifying ANY frontend code (components, hooks, pages, API calls, styling).
>
> These skills contain project-specific patterns and conventions. Skipping them will result in inconsistent code that doesn't follow project standards. Load the skill FIRST, then implement.

### Slash Commands

| Command | Purpose |
|---------|---------|
| `/dev-docs [description]` | Create strategic plan with task breakdown |
| `/dev-docs-update` | Update dev documentation before context compaction |

### Agents (Via Task tool)

| Agent | Purpose |
|-------|---------|
| `code-architecture-reviewer` | Review code for best practices and patterns |
| `code-refactor-master` | Execute refactoring with dependency tracking |
| `plan-reviewer` | Review plans before implementation |
| `refactor-planner` | Create comprehensive refactoring plans |

## Development Workflow

### Starting a New Feature

1. Use `/dev-docs [feature description]` to create plan
2. Plan creates `dev/active/[feature]/` with three files:
   - `[feature]-plan.md` - Strategic implementation plan
   - `[feature]-context.md` - Current state, decisions, blockers
   - `[feature]-tasks.md` - Checkbox task list
3. Work through tasks, updating context frequently

### Before Context Compaction

Run `/dev-docs-update` to save current state to dev docs.

### Resuming Work

1. Read `dev/active/[task]/[task]-context.md` first
2. Check SESSION PROGRESS section for current state
3. Continue from documented position

## Key Conventions

### Backend (FastAPI)

- **Routes:** Thin controllers, delegate to services via `Depends()`
- **Services:** Business logic, injected via FastAPI DI
- **CRUD:** Database operations only, no business logic
- **Schemas:** All I/O through Pydantic models
- **Config:** Pydantic Settings, never raw `os.environ`
- **Errors:** Log to Sentry, return HTTPException

### Frontend (React)

- **Components:** `React.FC<Props>` pattern
- **Data:** `useSuspenseQuery` with Suspense boundaries
- **Loading:** Use Suspense, avoid early returns
- **Styling:** Mantine components + theme context
- **Organization:** Feature-based structure in `src/features/`

### Database

- **Migrations:** Alembic, never modify production directly
- **Sessions:** Async via dependency injection
- **Models:** SQLAlchemy 2.0 style with type hints

## Running the Project

```bash
# Start all services
docker compose up --build

# Access points
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```
GEMINI_API_KEY=your_key_here  # Required
```

## Current Status

- [x] Backend skeleton (FastAPI, config, health endpoint)
- [x] Docker Compose configuration
- [x] Database setup (PostgreSQL)
- [x] Database models (User, Word, GrammarTopic, TopicProgress, ExerciseLog, ErrorLog, Session)
- [x] Enums (PartOfSpeech, Gender, CEFRLevel, ExerciseType, ErrorCategory)
- [x] Pydantic schemas (User, Word, GrammarTopic, Progress, Exercise)
- [x] Alembic migrations
- [x] CRUD operations (Word, GrammarTopic, TopicProgress, Session)
- [x] API routes (Words, Drills, Topics, Exercises, Progress, Sessions, Analytics)
- [x] Gemini service integration (chat sessions, exercise generation)
- [x] Frontend (React + Mantine UI)
- [x] All exercise types (Translation, Grammar, Reading, Dialogue, Sentence Construction)
- [x] Progress tracking dashboard
- [x] Analytics (leeches, forecast, velocity, difficulty)

## Data Model

### Core Models
- **User** - Learner profile with CEFR level, preferences
- **Word** - Vocabulary entries with Croatian/English, part of speech, gender, proficiency tracking
- **GrammarTopic** - Grammar rules and explanations organized by CEFR level
- **Session** - Learning session tracking

### Progress Tracking
- **TopicProgress** - Per-user mastery of grammar topics
- **ExerciseLog** - History of completed exercises with scores
- **ErrorLog** - Tracked errors for pattern analysis and targeted practice

### Enums
- **CEFRLevel** - A1, A2, B1, B2, C1, C2
- **PartOfSpeech** - noun, verb, adjective, adverb, pronoun, preposition, conjunction, interjection, numeral, particle, phrase
- **Gender** - masculine, feminine, neuter
- **ExerciseType** - vocabulary_cr_en, vocabulary_en_cr, vocabulary_fill_blank, conversation, grammar, sentence_construction, reading, dialogue, translation_cr_en, translation_en_cr
- **ErrorCategory** - case_error, gender_agreement, verb_conjugation, word_order, spelling, vocabulary, accent, other
