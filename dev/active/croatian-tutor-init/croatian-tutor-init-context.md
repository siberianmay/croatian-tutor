# Croatian Language Tutor - Project Context

**Last Updated: 2025-11-22**

---

## Key Decisions Made

### Technology Choices

| Decision | Choice | Rationale | Alternatives Considered |
|----------|--------|-----------|------------------------|
| Backend Framework | FastAPI | Async, auto-docs, typing, fast | Flask, Django |
| Frontend Framework | React + Vite | Fast dev, modern tooling | Next.js, Vue |
| UI Component Library | Mantine | Beautiful defaults, great DX | Chakra, MUI, Tailwind |
| Database | PostgreSQL | JSON support, arrays, mature | MySQL |
| ORM | SQLAlchemy 2.0 | Async support, industry standard | Tortoise ORM |
| AI Service | Gemini API | User requirement | OpenAI, Claude |
| Containerization | Docker Compose | Simple local orchestration | Kubernetes (overkill) |

### Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | None | Single user, local only |
| API Style | REST | Simpler than GraphQL for this scope |
| State Management | TanStack Query | Server state caching, no Redux needed |
| Python Version | 3.12+ | Latest features, performance |
| Node Version | 20 LTS | Stability |

---

## Project Constraints

1. **Local Only**: No cloud deployment, no external access
2. **Single User**: No authentication, no multi-tenancy
3. **Gemini Dependency**: Core functionality requires API availability
4. **Docker Required**: All services must run in containers

---

## External Dependencies

### APIs
| Service | Purpose | Documentation |
|---------|---------|---------------|
| Gemini API | AI tutor, exercise generation, evaluation | https://ai.google.dev/docs |

### Key Libraries (Backend)
| Library | Version | Purpose |
|---------|---------|---------|
| fastapi | Latest | Web framework |
| sqlalchemy | 2.0+ | ORM |
| alembic | Latest | Migrations |
| asyncpg | Latest | Async PostgreSQL driver |
| pydantic | 2.0+ | Validation |
| google-generativeai | Latest | Gemini SDK |
| httpx | Latest | Async HTTP client |
| uvicorn | Latest | ASGI server |

### Key Libraries (Frontend)
| Library | Version | Purpose |
|---------|---------|---------|
| react | 18+ | UI framework |
| @mantine/core | 7+ | UI components |
| @mantine/hooks | 7+ | Utility hooks |
| @tanstack/react-query | 5+ | Data fetching |
| react-router-dom | 6+ | Routing |
| axios | Latest | HTTP client |
| typescript | 5+ | Type safety |

---

## Environment Variables

```bash
# Backend
DATABASE_URL=postgresql+asyncpg://croatian:tutor_local@db:5432/croatian_tutor
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## Key Files Reference

Once project is scaffolded:

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Service orchestration |
| `.env` | Environment variables (gitignored) |
| `.env.example` | Template for env vars |
| `backend/app/main.py` | FastAPI entry point |
| `backend/app/config.py` | Settings/config management |
| `backend/app/services/gemini_service.py` | Gemini API integration |
| `frontend/src/App.tsx` | React entry component |
| `frontend/src/api/client.ts` | API client configuration |

---

## Database Schema Relationships

```
topics (1) ──────────────────── (N) words
   │                                  │
   │                                  │
   └──── (1) ─────── (N) exercises    └──── (1) ─────── (1) word_progress
                          │
                          │
         learning_sessions (1) ─────── (N) exercises (via session_id FK - optional)
```

---

## Gemini Prompt Templates

### Base System Prompt
```
You are a Croatian language tutor. Respond ONLY in valid JSON format.
Student level: {level}
Known vocabulary count: {word_count}
Current focus topics: {topics}
Recent performance: {performance_summary}
```

### Exercise Generation
```json
{
  "request": "generate_exercise",
  "type": "{exercise_type}",
  "difficulty": "{difficulty}",
  "topic": "{topic}",
  "avoid_words": ["{recently_used_words}"],
  "focus_words": ["{words_needing_practice}"]
}
```

### Response Format (Exercise)
```json
{
  "exercise": {
    "type": "vocabulary_translation",
    "direction": "en_to_hr",
    "prompt": "Translate: 'Good morning'",
    "expected_answer": "Dobro jutro",
    "acceptable_alternatives": ["Jutro"],
    "hints": ["Think about 'good' + time of day"],
    "difficulty": 1
  }
}
```

### Response Format (Evaluation)
```json
{
  "evaluation": {
    "is_correct": true,
    "score": 1.0,
    "feedback": "Perfect! 'Dobro jutro' is the standard greeting.",
    "corrections": [],
    "tips": ["You can also use just 'Jutro' informally"],
    "next_recommendation": "Try a harder greeting exercise"
  }
}
```

---

## Common Patterns

### Backend API Pattern
```python
# routes/words.py
@router.get("/", response_model=list[WordResponse])
async def list_words(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    return await word_crud.get_multi(db, skip=skip, limit=limit)
```

### Frontend Query Pattern
```typescript
// hooks/useWords.ts
export function useWords() {
  return useQuery({
    queryKey: ['words'],
    queryFn: () => api.get<Word[]>('/api/v1/words').then(r => r.data)
  });
}
```

---

## Risk Mitigations

| Risk | Mitigation Strategy |
|------|---------------------|
| Gemini API down | Cache recent exercises, show cached content |
| Gemini response parsing fails | Retry with simplified prompt, fallback to static exercises |
| Rate limiting | Implement request queuing, cache responses |
| Schema changes | Always use Alembic, never modify DB directly |

---

## Testing Strategy

### Backend
- Unit tests for services (mocked Gemini)
- Integration tests for API endpoints
- Use pytest-asyncio for async tests

### Frontend
- Component tests with Vitest
- E2E tests with Playwright (optional, Phase 5)

---

## Notes for Future Development

1. **Audio Support**: Consider ElevenLabs or Google TTS for pronunciation
2. **Spaced Repetition**: SM-2 algorithm for word review scheduling
3. **Export**: Allow exporting vocabulary to Anki format
4. **Backup**: Add DB backup script to docker-compose
5. **Mobile**: Mantine is responsive, mobile-friendly by default
