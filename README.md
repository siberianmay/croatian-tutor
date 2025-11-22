# Croatian Language Tutor

AI-powered Croatian language learning application using Gemini as an intelligent tutor.

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Gemini API key (get from https://makersuite.google.com/app/apikey)

### Setup

1. Copy environment file and add your Gemini API key:
```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

2. Start all services:
```bash
docker compose up --build
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development

#### Backend (FastAPI)
```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

#### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │───▶│   Backend    │───▶│  PostgreSQL  │
│ React+Mantine│    │   FastAPI    │    │   Database   │
│  Port 3000   │    │  Port 8000   │    │  Port 5432   │
└──────────────┘    └──────┬───────┘    └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  Gemini API  │
                   └──────────────┘
```

## Project Structure

```
croatian-tutor/
├── docker-compose.yml
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   │   ├── user.py           # User profile
│   │   │   ├── word.py           # Vocabulary entries
│   │   │   ├── grammar_topic.py  # Grammar rules
│   │   │   ├── topic_progress.py # Grammar mastery
│   │   │   ├── exercise_log.py   # Exercise history
│   │   │   ├── error_log.py      # Error tracking
│   │   │   ├── session.py        # Learning sessions
│   │   │   └── enums.py          # CEFRLevel, PartOfSpeech, etc.
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic + Gemini
│   │   └── crud/         # Database operations
│   └── alembic/          # Database migrations
└── frontend/             # React application (planned)
    └── src/
        ├── components/
        ├── pages/
        ├── api/
        └── hooks/
```

## Features

- Vocabulary tracking with proficiency scores
- AI-generated exercises tailored to your level
- Answer evaluation with detailed feedback
- Progress tracking and learning recommendations
- Topic-based learning organization

## Data Model

The application uses CEFR levels (A1-C2) to track and adapt to learner progress:

- **User** - Learner profile with current CEFR level and preferences
- **Word** - Vocabulary with Croatian/English, part of speech, gender, difficulty level
- **GrammarTopic** - Grammar rules organized by CEFR level
- **TopicProgress** - Mastery tracking per grammar topic
- **ExerciseLog** - Exercise history with scores
- **ErrorLog** - Error pattern tracking for targeted practice
- **Session** - Learning session management

### Exercise Types
- Vocabulary drills (Croatian↔English, fill-in-blank)
- Grammar exercises
- Translation practice
- Conversation with AI tutor
- Reading comprehension
- Sentence construction

## Current Status

| Component | Status |
|-----------|--------|
| Backend skeleton | ✅ Complete |
| Docker Compose | ✅ Complete |
| Database setup | ✅ Complete |
| SQLAlchemy models | ✅ Complete |
| Pydantic schemas | ✅ Complete |
| Alembic migrations | ✅ Complete |
| CRUD operations | 🔄 In progress |
| API routes | ⬜ Pending |
| Gemini integration | ⬜ Pending |
| Frontend | ⬜ Pending |
