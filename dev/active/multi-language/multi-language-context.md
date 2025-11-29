# Multi-Language Support - Context Document

**Last Updated:** 2025-11-29

## Key Files

### Backend Models
| File | Purpose | Changes Needed  |
|------|---------|-----------------|
| `backend/app/models/language.py` | Language model | Already exists  |
| `backend/app/models/word.py` | Vocabulary | Add language FK |
| `backend/app/models/grammar_topic.py` | Grammar rules | Add language FK |
| `backend/app/models/session.py` | Exercise sessions | Add language FK |
| `backend/app/models/exercise_log.py` | Daily activity | Add language FK |
| `backend/app/models/error_log.py` | Error tracking | Add language FK |
| `backend/app/models/user.py` | User profile | Add language FK |

### Backend Schemas
| File | Purpose | Changes Needed |
|------|---------|--------------|
| `backend/app/schemas/language.py` | Language schemas | Add LanguageResponse |
| `backend/app/schemas/word.py` | Word schemas | Add language to create/update |
| `backend/app/schemas/grammar_topic.py` | Topic schemas | Add language |
| `backend/app/schemas/user.py` | User schemas | Add language |

### Backend CRUD
| File | Purpose | Changes Needed |
|------|---------|--------------|
| `backend/app/crud/word.py` | Word operations | Add language filter |
| `backend/app/crud/grammar_topic.py` | Topic operations | Add language filter |
| `backend/app/crud/session.py` | Session operations | Add language |
| NEW: `backend/app/crud/language.py` | Language operations | Create |

### Backend API
| File | Purpose | Changes Needed |
|------|---------|----------------|
| `backend/app/api/words.py` | Word endpoints | Use language from user |
| `backend/app/api/drills.py` | Drill endpoints | Use language from user |
| `backend/app/api/exercises.py` | Exercise endpoints | Use language from user |
| `backend/app/api/topics.py` | Topic endpoints | Filter by language |
| `backend/app/api/progress.py` | Progress endpoints | Filter by language |
| `backend/app/api/analytics.py` | Analytics endpoints | Filter by language |
| `backend/app/api/settings.py` | Settings endpoints | Add language get/set |
| NEW: `backend/app/api/languages.py` | Language endpoints | Create |

### Backend Services
| File | Purpose | Changes Needed |
|------|---------|----------------|
| `backend/app/services/gemini_service.py` | AI prompts | Parameterize language |
| `backend/app/services/exercise_service.py` | Exercise logic | Pass language to Gemini |
| `backend/app/services/drill_service.py` | Drill logic | Pass language to Gemini |

### Frontend Pages
| File | Purpose | Changes Needed |
|------|---------|----------------|
| `frontend/src/pages/SettingsPage.tsx` | User settings | Add language selector |
| `frontend/src/pages/VocabularyPage.tsx` | Vocab list | Dynamic language labels |
| `frontend/src/pages/GrammarTopicsPage.tsx` | Grammar list | Dynamic language labels |
| `frontend/src/pages/PracticePage.tsx` | Exercise hub | Dynamic language labels |
| `frontend/src/pages/LearnPage.tsx` | Conversation | Dynamic language labels |
| `frontend/src/pages/ProgressPage.tsx` | Progress dashboard | Dynamic language labels |

### Frontend Services
| File | Purpose | Changes Needed |
|------|---------|----------------|
| NEW: `frontend/src/services/languageApi.ts` | Language API | Create |
| `frontend/src/services/settingsApi.ts` | Settings API | Add language methods |

### Frontend Types
| File | Purpose | Changes Needed |
|------|---------|----------------|
| `frontend/src/types/index.ts` | Type definitions | Add Language, update Word, etc. |

### Migrations
| File | Purpose | Status |
|------|---------|--------|
| `c1d1e1f1a1b1_add_language_table.py` | Language table | ✅ Applied |
| `d2e2f2a2b2c2_add_language_to_tables.py` | Add FKs to tables | ✅ Applied |

---

## Current Database State

### Language Table (Exists)
```sql
CREATE TABLE language (
    code VARCHAR(8) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
-- Seeded: ('hr', 'Croatian', 'Hrvatski', true)
```

### Tables With language Column (✅ All Applied)

1. **word** - `language` VARCHAR(8) FK, default 'hr'
2. **grammar_topic** - `language` VARCHAR(8) FK, default 'hr', unique(name, language)
3. **session** - `language` VARCHAR(8) FK, default 'hr'
4. **exercise_log** - `language` VARCHAR(8) FK, default 'hr', unique(user_id, date, exercise_type, language)
5. **error_log** - `language` VARCHAR(8) FK, default 'hr'
6. **user** - `language` VARCHAR(8) FK, default 'hr'

---

## Decisions Made

1. **Language code as PK**: Using string code (e.g., 'hr', 'es') as primary key rather than integer ID
2. **Default language**: Croatian ('hr') is default for all existing data and new users
3. **User-level setting**: Language selection is per-user, not app-wide
4. **TopicProgress**: Will inherit language from GrammarTopic (no direct FK needed)
5. **Word column names**: Keeping `croatian`/`english` for now; renaming deferred to future refactor

## Decisions Pending

- [ ] How to handle language switching with in-progress exercises
- [ ] Whether to add language filter UI to vocabulary/topic list pages
- [ ] How to seed grammar topics for new languages

---

## Dependencies

### Migration Order
1. Language table exists (already done)
2. Add language code to all tables in single migration
3. All existing data defaults to 'hr'

### Code Deployment Order
1. Run migration first
2. Deploy backend changes
3. Deploy frontend changes

---

## SESSION PROGRESS

### Current State (2025-11-29)
- ✅ Phase 1: Database Schema Updates - COMPLETE
  - Migration `d2e2f2a2b2c2_add_language_to_tables.py` applied
  - All models updated with `language` column
  - Relationships use `language_ref` (to avoid naming conflict with column)
  - Migration upgrade/downgrade tested successfully

- ✅ Phase 2: Backend Model & Schema Updates - COMPLETE
  - Pydantic schemas updated (WordResponse, GrammarTopicResponse, UserResponse)
  - LanguageResponse schema created
  - Language CRUD and API created (`/api/v1/languages`)

- ✅ Phase 3: CRUD Layer Updates - COMPLETE
  - WordCRUD: All methods updated with language filter
  - GrammarTopicCRUD: All methods updated with language filter
  - TopicProgressCRUD: All methods updated with language filter (via join)
  - SessionCRUD: All methods updated with language parameter
  - UserCRUD: Created with get_language/set_language methods

- 🔄 Phase 4: API Layer Updates - IN PROGRESS
  - ✅ Created `app/api/dependencies.py` with `get_current_language()` dependency
  - ✅ Updated Words API with language injection
  - ✅ Updated Topics API with language injection
  - ✅ Updated Drills API with language injection
  - ✅ Updated DrillService with language parameter
  - ⏳ Exercises API, Progress API, Analytics API, Settings API still pending

### Next Steps
1. Update remaining APIs (exercises, progress, analytics, settings)
2. Phase 5: Gemini Service Updates (language in prompts)
3. Phase 6-7: Frontend updates

### Blockers
None currently identified.

### Notes
- Column is named `language` (not `language_code`) for simplicity
- Relationship is named `language_ref` to avoid conflict with column name
- User model has `language` column and `selected_language` relationship
- `get_current_language()` dependency reads from user's saved language preference
