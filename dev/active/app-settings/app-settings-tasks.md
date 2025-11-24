# Application Settings - Task Checklist

**Last Updated:** 2025-11-24

## Phase 1: Backend Database Layer

- [x] Create `backend/app/models/app_settings.py`
  - AppSettings model with SQLAlchemy 2.0 syntax
  - Fields: id, grammar_batch_size, translation_batch_size, reading_passage_length, gemini_model, updated_at
  - Defaults defined in model

- [x] Update `backend/app/models/__init__.py`
  - Import and export AppSettings

- [x] Create Alembic migration
  - Created: `b2c3d4e5f6a7_add_app_settings_table.py`
  - Creates table with proper constraints
  - Inserts default row (id=1)

- [x] Test migration
  - Run: `alembic upgrade head`
  - Verify table exists with default row

## Phase 2: Backend Schemas & CRUD

- [x] Create `backend/app/schemas/app_settings.py`
  - AppSettingsResponse: All fields + updated_at
  - AppSettingsUpdate: All fields optional, with validators for ranges
  - GeminiModel validation against enum values

- [x] Create `backend/app/crud/app_settings.py`
  - `get()`: Fetch settings (id=1), auto-create if missing
  - `update()`: Partial update, return updated row

## Phase 3: Backend API

- [x] Create `backend/app/api/settings.py`
  - `GET /settings` - Return current settings
  - `PATCH /settings` - Update settings (partial)
  - `GET /settings/models` - Return available Gemini models
  - Proper dependency injection

- [x] Update `backend/app/api/router.py`
  - Import settings router
  - Included in api_router

- [x] Test API endpoints
  - GET returns defaults
  - PATCH updates individual fields
  - Invalid values return 422

## Phase 4: Backend Service Integration

- [x] Update `GeminiService` in `backend/app/services/gemini_service.py`
  - Added `set_model()` method to configure model
  - Added `_get_model()` to return configured or default model
  - Removed random model selection
  - Default model: gemini-2.5-flash

- [x] Update `ExerciseService` in `backend/app/services/exercise_service.py`
  - `generate_reading_exercise()` now accepts `passage_length` parameter
  - Calculates min/max range around target length

- [x] Update exercise API endpoints
  - `get_exercise_service()` now fetches settings and configures Gemini
  - Reading endpoint passes `reading_passage_length` from settings

## Phase 5: Frontend Settings Page

- [x] Add types to `frontend/src/types/index.ts`
  - GeminiModel type
  - AppSettings interface
  - AppSettingsUpdate interface

- [x] Create `frontend/src/services/settingsApi.ts`
  - get(): GET /api/settings
  - update(): PATCH /api/settings
  - getAvailableModels(): GET /api/settings/models

- [x] Create `frontend/src/pages/SettingsPage.tsx`
  - NumberInput for batch sizes (3-20)
  - Slider for passage length (100-1000)
  - Select dropdown for Gemini model
  - Save button with loading state
  - Success/error notifications
  - Reset to defaults button

- [x] Update `frontend/src/App.tsx`
  - Lazy import SettingsPage
  - Added route: `/settings`

- [x] Update `frontend/src/components/layout/AppLayout.tsx`
  - Added Settings nav item with IconSettings
  - Positioned at bottom of nav (after Progress)

## Phase 6: Testing & Polish

- [x] Manual testing
  - Change settings, verify exercises use new values
  - Verify reading passages match configured length (approximately)
  - Verify Gemini model is used (check logs)

- [ ] Error handling
  - Network errors on settings page
  - Invalid model name handling

## Completion Criteria

- [x] All 4 settings configurable via UI
- [x] Settings persist in database (need to run migration)
- [x] Grammar/Translation batch sizes use settings as defaults
- [x] Reading passage length follows configured value
- [x] Gemini model is deterministic (not random)
- [ ] No regressions in existing functionality (need to test)
