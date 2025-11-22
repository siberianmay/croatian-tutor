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
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── crud/     # Database operations
│   └── alembic/      # Database migrations
└── frontend/          # React application
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
