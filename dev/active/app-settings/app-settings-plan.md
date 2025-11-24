# Application Settings Feature - Implementation Plan

**Last Updated:** 2025-11-24

## Executive Summary

Add persistent application settings to control:
- Grammar exercise batch size (default: 10)
- Translation exercise batch size (default: 10)
- Reading comprehension passage length (default: 200-500 chars)
- Gemini model selection (currently random from enum)

These settings will be stored in a database table and exposed via API + frontend Settings page.

---

## Current State Analysis

### Backend
- **GeminiService** (`backend/app/services/gemini_service.py`):
  - `GeminiModel` enum exists with 5 models: `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-2.5-pro`
  - Model is selected randomly via `random.choice()` in `_model` property (line 53)
  - No configuration mechanism exists

- **ExerciseService** (`backend/app/services/exercise_service.py`):
  - `generate_grammar_exercises_batch()`: `count=10` default (line 324)
  - `generate_translation_exercises_batch()`: `count=10` default (line 638)
  - `generate_reading_exercise()`: Hardcoded prompt "200-500 characters" (line 993-994)

- **Exercises API** (`backend/app/api/exercises.py`):
  - `GrammarBatchRequest.count`: `Field(default=10, ge=1, le=20)`
  - `TranslationBatchRequest.count`: `Field(default=10, ge=1, le=20)`
  - No settings integration

- **User Model** (`backend/app/models/user.py`):
  - Stores `preferred_cefr_level` and `daily_goal_minutes`
  - Single user design (id=1)

### Frontend
- No settings page exists
- Navigation in `AppLayout.tsx` has 5 items: Learn, Flashcards, Vocabulary, Grammar, Progress
- Uses React + Mantine UI + TanStack Query

---

## Proposed Future State

### Database
New `app_settings` table (singleton pattern - single row with id=1):
```
app_settings:
  - id: 1 (primary key)
  - grammar_batch_size: int (default: 10, range: 3-20)
  - translation_batch_size: int (default: 10, range: 3-20)
  - reading_passage_length: int (default: 350, range: 100-1000)
  - gemini_model: str (default: "gemini-2.5-flash")
  - updated_at: datetime
```

### Backend
- New SQLAlchemy model: `AppSettings`
- New Pydantic schemas: `AppSettingsRead`, `AppSettingsUpdate`
- New CRUD: `AppSettingsCRUD` with `get()` and `update()` methods
- New API: `GET /api/settings`, `PATCH /api/settings`
- Update `GeminiService` to accept model parameter
- Update `ExerciseService` to fetch settings and use them

### Frontend
- New Settings page at `/settings`
- Add "Settings" nav item with gear icon
- Form with inputs for all 4 settings
- API service for settings CRUD

---

## Implementation Phases

### Phase 1: Backend Database Layer (Effort: M)
Create the database model and migration.

**Tasks:**
1. Create `backend/app/models/app_settings.py` with `AppSettings` model
2. Add export to `backend/app/models/__init__.py`
3. Create Alembic migration for `app_settings` table
4. Create seed data (insert default row with id=1)

**Acceptance Criteria:**
- Model uses SQLAlchemy 2.0 mapped_column syntax
- Migration creates table with proper constraints
- Default row exists after migration

### Phase 2: Backend Schemas & CRUD (Effort: S)
Create Pydantic schemas and CRUD operations.

**Tasks:**
1. Create `backend/app/schemas/app_settings.py` with `AppSettingsRead`, `AppSettingsUpdate`
2. Create `backend/app/crud/app_settings.py` with `get()` and `update()` methods

**Acceptance Criteria:**
- Schemas validate ranges (batch sizes: 3-20, passage length: 100-1000)
- CRUD handles upsert pattern for singleton
- `GeminiModel` enum values validated in schema

### Phase 3: Backend API (Effort: S)
Create API endpoints for settings.

**Tasks:**
1. Create `backend/app/api/settings.py` with GET/PATCH endpoints
2. Register router in `backend/app/api/router.py`

**Acceptance Criteria:**
- `GET /api/settings` returns current settings
- `PATCH /api/settings` updates specified fields only
- Proper validation error responses

### Phase 4: Backend Service Integration (Effort: M)
Update services to use settings.

**Tasks:**
1. Update `GeminiService` to accept `model_name` parameter in generation methods
2. Update `ExerciseService` to fetch settings and pass to Gemini
3. Update reading exercise prompt to use configurable passage length
4. Add settings dependency to exercise API endpoints

**Acceptance Criteria:**
- Gemini uses configured model instead of random
- Batch sizes respect settings when frontend doesn't specify
- Reading passage length prompt uses setting value

### Phase 5: Frontend Settings Page (Effort: M)
Create the Settings UI.

**Tasks:**
1. Create `frontend/src/services/settingsApi.ts`
2. Create `frontend/src/types/settings.ts`
3. Create `frontend/src/pages/SettingsPage.tsx`
4. Add route to `App.tsx`
5. Add "Settings" to navigation in `AppLayout.tsx`

**Acceptance Criteria:**
- Settings page displays current values
- Form validates input ranges
- Success/error feedback on save
- Settings icon in nav (IconSettings from tabler)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration fails on existing DB | High | Use `if not exists` pattern; test on copy first |
| Gemini model name validation | Medium | Validate against enum values; fallback to default |
| Settings not found (deleted row) | Medium | CRUD auto-creates default on `get()` if missing |
| Performance (extra DB query per exercise) | Low | Cache settings in memory with short TTL or fetch once per request |

---

## Success Metrics

1. All 4 settings are configurable via UI
2. Settings persist across application restarts
3. Exercises use configured batch sizes when not overridden
4. Reading passages match configured length
5. Gemini model is deterministic (not random)

---

## Dependencies

- Alembic for migrations
- No new Python packages required
- No new npm packages required

---

## Technical Notes

### Singleton Pattern
The `app_settings` table uses a singleton pattern (id=1 always). The CRUD layer should:
1. Always query for id=1
2. Auto-create row if missing
3. Never allow row deletion

### Model Selection
The `GeminiModel` enum values should be stored as strings in the database to allow future model additions without migration.

### Default Behavior
When settings are not yet configured:
- Grammar batch: 10
- Translation batch: 10
- Reading passage: 350 chars (middle of 200-500 range)
- Gemini model: `gemini-2.5-flash` (good balance of speed/quality)
