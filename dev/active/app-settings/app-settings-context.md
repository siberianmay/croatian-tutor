# Application Settings - Context & Decisions

**Last Updated:** 2025-11-24

## Key Files

### Backend - Models
- `backend/app/models/app_settings.py` (to create)
- `backend/app/models/__init__.py` - Export AppSettings
- `backend/app/models/enums.py` - Contains GeminiModel if moved here

### Backend - Schemas
- `backend/app/schemas/app_settings.py` (to create)

### Backend - CRUD
- `backend/app/crud/app_settings.py` (to create)

### Backend - API
- `backend/app/api/settings.py` (to create)
- `backend/app/api/router.py` - Register settings router

### Backend - Services
- `backend/app/services/gemini_service.py` - GeminiModel enum, _model property
- `backend/app/services/exercise_service.py` - Batch generation methods

### Frontend
- `frontend/src/pages/SettingsPage.tsx` (to create)
- `frontend/src/services/settingsApi.ts` (to create)
- `frontend/src/types/settings.ts` (to create)
- `frontend/src/App.tsx` - Add route
- `frontend/src/components/layout/AppLayout.tsx` - Add nav item

### Database
- `backend/alembic/versions/` - New migration file

---

## Architecture Decisions

### Decision 1: Singleton Table vs User Settings
**Choice:** Singleton `app_settings` table (id=1)
**Rationale:**
- Single-user app design (DEFAULT_USER_ID = 1 throughout)
- Simpler model
- If multi-user needed later, can migrate settings to User model

### Decision 2: Where to Store GeminiModel Enum
**Choice:** Keep in `gemini_service.py`, store string in DB
**Rationale:**
- Enum already exists there
- Storing string allows adding models without migration
- Validation happens at schema level

### Decision 3: Settings Fetch Strategy
**Choice:** Fetch settings once per request via dependency injection
**Rationale:**
- Avoids multiple DB calls in a request
- Request-scoped caching is sufficient
- No need for Redis/in-memory caching for single-user app

### Decision 4: Default Values Location
**Choice:** Defaults in model definition (SQLAlchemy defaults)
**Rationale:**
- Single source of truth
- Applied automatically on insert
- Migration seeds with these defaults

---

## Current Session Progress

### Completed
- [x] Analyzed existing codebase
- [x] Created implementation plan
- [x] Created context document
- [x] Created task checklist

### In Progress
- [ ] Waiting for implementation approval

### Blocked
- None

---

## API Contract

### GET /api/settings
```json
{
  "grammar_batch_size": 10,
  "translation_batch_size": 10,
  "reading_passage_length": 350,
  "gemini_model": "gemini-2.5-flash",
  "updated_at": "2025-11-24T12:00:00Z"
}
```

### PATCH /api/settings
Request (partial update):
```json
{
  "grammar_batch_size": 15,
  "gemini_model": "gemini-2.5-pro"
}
```

Response: Same as GET

---

## Validation Rules

| Field | Type | Min | Max | Default |
|-------|------|-----|-----|---------|
| grammar_batch_size | int | 5 | 20 | 10 |
| translation_batch_size | int | 5 | 20 | 10 |
| reading_passage_length | int | 100 | 1000 | 350 |
| gemini_model | enum | - | - | gemini-2.5-flash |

### Valid Gemini Models
- `gemini-2.0-flash`
- `gemini-2.0-flash-lite`
- `gemini-2.5-flash-lite`
- `gemini-2.5-flash`
- `gemini-2.5-pro`

---

## Notes & Observations

1. **Exercise batch endpoints** already accept `count` parameter - settings provide defaults when not specified
2. **Reading exercise** hardcodes "200-500 characters" in prompt - will make this dynamic
3. **GeminiService singleton** - need to consider how to inject settings (method parameter vs constructor)
4. **Frontend exercise pages** may need to read settings to show configured batch size

---

## Open Questions

1. Should frontend exercise pages display/use the configured batch sizes?
   - **Tentative:** Yes, fetch settings and use as default

2. Should we add a "Reset to Defaults" button on settings page?
   - **Tentative:** Yes, good UX

3. Should we validate Gemini model availability via API call?
   - **Tentative:** No, trust enum - API errors will surface invalid models
