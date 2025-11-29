# Multi-Language Support Implementation Plan

**Last Updated:** 2025-11-29

## Executive Summary

Transform the Croatian language tutor application into a multi-language learning platform. Users will select a target language in settings, and all drills, exercises, grammar topics, and vocabulary will be scoped to that language. This requires database schema changes, backend query modifications, frontend state management, and Gemini prompt updates.

## Current State Analysis

### Database Models (No language scoping)
- **Word** (`backend/app/models/word.py`): Vocabulary tied to user, no language field
- **GrammarTopic** (`backend/app/models/grammar_topic.py`): Grammar rules, no language field
- **Session** (`backend/app/models/session.py`): Exercise sessions, no language field
- **ExerciseLog** (`backend/app/models/exercise_log.py`): Daily activity, no language field
- **ErrorLog** (`backend/app/models/error_log.py`): Error tracking, no language field
- **TopicProgress** (`backend/app/models/topic_progress.py`): Links user to topic, inherits language from topic

### Language Infrastructure (Already created)
- **Language** model exists (`backend/app/models/language.py`): `code` (PK), `name`, `native_name`, `is_active`
- **Migration** exists (`c1d1e1f1a1b1_add_language_table.py`): Seeds Croatian as "hr"
- **Schema** exists (`backend/app/schemas/language.py`): `LanguageBase`, `LanguageCreate`

### User Settings
- **User** model: Has `preferred_cefr_level`, `daily_goal_minutes` - needs `selected_language_code`
- **AppSettings** model: Singleton for app-wide settings - not suitable for language (user-level)

### Frontend
- All pages assume Croatian
- No language selector component
- Hardcoded references to "Croatian" in UI text
- **SettingsPage.tsx**: Currently only has exercise/AI settings

### Gemini Service
- Prompts explicitly mention "Croatian"
- Would need language parameter to generate content for other languages

## Proposed Future State

### 1. Database Schema
- Add `language_code` FK to: `word`, `grammar_topic`, `session`, `exercise_log`, `error_log`
- Add `selected_language_code` to `user` model (default: 'hr')
- All queries filter by user's selected language

### 2. Backend
- All CRUD operations accept `language_code` parameter
- All API endpoints derive language from user's setting or explicit parameter
- Gemini prompts dynamically include target language name

### 3. Frontend
- Language selector in Settings page
- Display selected language in UI
- All exercise pages work with selected language
- Language-aware labels (not hardcoded "Croatian")

---

## Implementation Phases

### Phase 1: Database Schema Updates
Add `language_code` foreign key to required tables with migration.

### Phase 2: Backend Model & Schema Updates
Update SQLAlchemy models and Pydantic schemas to include language_code.

### Phase 3: CRUD Layer Updates
Modify all CRUD operations to filter by language_code.

### Phase 4: API Layer Updates
Update all API endpoints to use user's selected language.

### Phase 5: Gemini Service Updates
Parameterize all prompts with language name instead of hardcoded "Croatian".

### Phase 6: Frontend Language Selection
Add language selector to Settings, store selection, use throughout app.

### Phase 7: Frontend UI Updates
Update all pages to use dynamic language names instead of hardcoded "Croatian".

### Phase 8: Testing & Polish
Verify all flows work with language switching, seed additional languages.

---

## Detailed Task Breakdown

### Phase 1: Database Schema Updates (Effort: M)

**1.1 Create migration for adding language_code columns**
- File: `backend/alembic/versions/[new]_add_language_code_to_tables.py`
- Add `language_code` FK to: `word`, `grammar_topic`, `session`, `exercise_log`, `error_log`
- Add `selected_language_code` to `user` table
- Default all existing records to 'hr' (Croatian)
- Acceptance: Migration runs without errors, existing data preserved

**1.2 Update unique constraints**
- `exercise_log` has unique constraint `(user_id, date, exercise_type)` - needs `language_code`
- `grammar_topic.name` is unique - needs to be unique per language
- Acceptance: Constraints updated without data loss

### Phase 2: Backend Model & Schema Updates (Effort: M)

**2.1 Update Word model**
- Add `language_code: Mapped[str]` with FK to `language.code`
- Add relationship to Language
- Acceptance: Model changes, app starts without errors

**2.2 Update GrammarTopic model**
- Add `language_code: Mapped[str]` with FK
- Update unique constraint on `name` to include `language_code`
- Acceptance: Model changes, app starts without errors

**2.3 Update Session model**
- Add `language_code: Mapped[str]` with FK
- Acceptance: Model changes

**2.4 Update ExerciseLog model**
- Add `language_code: Mapped[str]` with FK
- Update unique constraint
- Acceptance: Model changes

**2.5 Update ErrorLog model**
- Add `language_code: Mapped[str]` with FK
- Acceptance: Model changes

**2.6 Update User model**
- Add `selected_language_code: Mapped[str]` with FK (default 'hr')
- Add relationship to Language
- Acceptance: Model changes

**2.7 Update Pydantic schemas**
- WordCreate/WordUpdate: Add optional `language_code`
- GrammarTopicCreate: Add `language_code`
- SessionCreate: Add `language_code`
- UserResponse: Add `selected_language_code`
- UserUpdate: Add `selected_language_code`
- Acceptance: Schemas validate correctly

**2.8 Add Language CRUD and API**
- Create `backend/app/crud/language.py`
- Create `backend/app/api/languages.py` with GET /languages endpoint
- Acceptance: Can fetch available languages via API

### Phase 3: CRUD Layer Updates (Effort: M)

**3.1 Update WordCRUD**
- All methods accept `language_code` parameter
- Queries filter by `language_code`
- Files: `backend/app/crud/word.py`
- Acceptance: All word queries are language-scoped

**3.2 Update GrammarTopicCRUD**
- `get_multi`, `get_by_name` filter by `language_code`
- Files: `backend/app/crud/grammar_topic.py`
- Acceptance: Topics filtered by language

**3.3 Update TopicProgressCRUD**
- Queries join through GrammarTopic to filter by language
- Acceptance: Progress scoped to language

**3.4 Update SessionCRUD**
- Add `language_code` to create method
- Filter sessions by language
- Files: `backend/app/crud/session.py`
- Acceptance: Sessions are language-scoped

**3.5 Add AppSettingsCRUD language methods**
- Get/set user's selected language
- Or add separate UserSettingsCRUD
- Acceptance: Can retrieve user's language preference

### Phase 4: API Layer Updates (Effort: L)

**4.1 Create language resolution dependency**
- FastAPI dependency that gets user's selected language
- Used across all exercise endpoints
- File: `backend/app/dependencies.py` or similar
- Acceptance: Dependency returns language_code

**4.2 Update Words API**
- `/words` endpoints use user's language
- `backend/app/api/words.py`
- Acceptance: Word endpoints language-scoped

**4.3 Update Drills API**
- `/drills` endpoints use user's language
- `backend/app/api/drills.py`
- Acceptance: Drills work with selected language

**4.4 Update Exercises API**
- All exercise generation uses user's language
- `backend/app/api/exercises.py`
- Acceptance: All exercise types generate for selected language

**4.5 Update Topics API**
- `/topics` returns language-filtered topics
- `backend/app/api/topics.py`
- Acceptance: Topics filtered by language

**4.6 Update Progress API**
- Progress endpoints scoped to language
- `backend/app/api/progress.py`
- Acceptance: Progress is language-specific

**4.7 Update Analytics API**
- Analytics scoped to user's language
- `backend/app/api/analytics.py`
- Acceptance: Analytics are language-specific

**4.8 Update Settings API**
- Add endpoint to get/set user's selected language
- `backend/app/api/settings.py`
- Acceptance: Can change language via API

### Phase 5: Gemini Service Updates (Effort: M)

**5.1 Add language parameter to GeminiService methods**
- `assess_word(croatian_word, language_name)`
- `assess_words_bulk(words, language_name)`
- `generate_fill_in_blank(..., language_name)`
- etc.
- File: `backend/app/services/gemini_service.py`
- Acceptance: All Gemini calls include language context

**5.2 Update all prompts**
- Replace hardcoded "Croatian" with `{language_name}`
- Update system instructions for chat sessions
- Acceptance: Prompts are language-dynamic

**5.3 Update ExerciseService**
- Pass language to Gemini service
- File: `backend/app/services/exercise_service.py`
- Acceptance: Exercises generate for correct language

**5.4 Update DrillService**
- Pass language to Gemini for fill-in-blank
- File: `backend/app/services/drill_service.py`
- Acceptance: Drills work with language

### Phase 6: Frontend Language Selection (Effort: M)

**6.1 Add Language types**
- `interface Language { code: string; name: string; native_name: string }`
- Update `AppSettings` or create `UserSettings` type
- File: `frontend/src/types/index.ts`
- Acceptance: Types defined

**6.2 Create languageApi service**
- `GET /languages` - fetch available languages
- `GET /settings/language` - get user's language
- `PATCH /settings/language` - set user's language
- File: `frontend/src/services/languageApi.ts`
- Acceptance: API calls work

**6.3 Create LanguageContext**
- React context for selected language
- Provides language code and name
- File: `frontend/src/contexts/LanguageContext.tsx`
- Acceptance: Context provides language info

**6.4 Update SettingsPage**
- Add language selector card
- Use languageApi to save selection
- Update LanguageContext on change
- File: `frontend/src/pages/SettingsPage.tsx`
- Acceptance: Can select language in settings

### Phase 7: Frontend UI Updates (Effort: L)

**7.1 Update VocabularyPage**
- Use dynamic language name in labels
- Column headers adapt to language
- File: `frontend/src/pages/VocabularyPage.tsx`
- Acceptance: No hardcoded "Croatian"

**7.2 Update GrammarTopicsPage**
- Dynamic language name
- File: `frontend/src/pages/GrammarTopicsPage.tsx`
- Acceptance: No hardcoded language

**7.3 Update PracticePage**
- Exercise descriptions use language name
- File: `frontend/src/pages/PracticePage.tsx`
- Acceptance: Dynamic language labels

**7.4 Update LearnPage**
- Conversation hints reference language
- File: `frontend/src/pages/LearnPage.tsx`
- Acceptance: Dynamic language

**7.5 Update ProgressPage**
- Stats show language context
- File: `frontend/src/pages/ProgressPage.tsx`
- Acceptance: Progress shows language

**7.6 Update navigation/header**
- Show selected language indicator
- File: Various layout files
- Acceptance: User sees current language

### Phase 8: Testing & Polish (Effort: S)

**8.1 Seed additional test languages**
- Add Spanish, German, French for testing
- File: migration or seed script
- Acceptance: Multiple languages available

**8.2 Test language switching flow**
- Switch language, verify data isolation
- Acceptance: Data properly separated

**8.3 Verify existing Croatian data works**
- All existing Croatian content still accessible
- Acceptance: No regression

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data migration breaks existing records | Low | High | Use server_default, NOT NULL with default |
| Gemini prompts fail with new language | Medium | Medium | Test with multiple languages, add validation |
| Foreign key constraints fail | Low | High | Ensure 'hr' language exists before migration |
| Frontend breaks due to missing context | Medium | Medium | Add LanguageContext provider at root |
| Performance degradation from extra joins | Low | Low | Indexes on language_code columns |

## Success Metrics

1. All existing Croatian data remains accessible and functional
2. User can select a different language in settings
3. All exercises generate content in selected language
4. Vocabulary is properly isolated per language
5. Grammar topics are properly isolated per language
6. Progress tracking is per-language
7. No hardcoded "Croatian" strings in UI

## Dependencies

- Language table must be seeded before migration runs
- User's language preference must be set before API calls
- LanguageContext must be available before pages render

## Required Resources

- Backend: Python/FastAPI developer
- Frontend: React/TypeScript developer
- Database: Alembic migrations
- AI: Gemini prompt engineering

## Notes

- The Word model currently has fields `croatian` and `english` - these should be renamed to `target_word` and `native_word` or similar in a future refactor, but that's out of scope for this phase.
- This implementation assumes a single "native" language (English) for all users. Multi-native-language support would require additional schema changes.
