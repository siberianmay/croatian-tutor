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

**Usage:** Invoke automatically when working on relevant code. Skills load architectural guidelines and patterns.

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
- [ ] Frontend scaffold
- [ ] Database models (Vocabulary, Exercise, Progress)
- [ ] Gemini service integration
- [ ] API routes
- [ ] UI implementation
