# Multi-Language Support - Task Checklist

**Last Updated:** 2025-11-29

## Phase 1: Database Schema Updates ✅ COMPLETE

- [x] 1.1 Create migration for adding language columns
  - [x] Add language FK to `word` table (default 'hr')
  - [x] Add language FK to `grammar_topic` table (default 'hr')
  - [x] Add language FK to `session` table (default 'hr')
  - [x] Add language FK to `exercise_log` table (default 'hr')
  - [x] Add language FK to `error_log` table (default 'hr')
  - [x] Add language FK to `user` table (default 'hr')
  - [x] Test migration upgrade
  - [x] Test migration downgrade

- [x] 1.2 Update unique constraints
  - [x] Update `exercise_log` unique constraint to include language
  - [x] Update `grammar_topic.name` unique constraint to include language
  - [x] Verify no constraint violations with existing data

## Phase 2: Backend Model & Schema Updates (IN PROGRESS)

- [x] 2.1 Update Word model (`backend/app/models/word.py`)
  - [x] Add language column with FK
  - [x] Add relationship to Language (`language_ref`)

- [x] 2.2 Update GrammarTopic model (`backend/app/models/grammar_topic.py`)
  - [x] Add language column with FK
  - [x] Add relationship to Language (`language_ref`)

- [x] 2.3 Update Session model (`backend/app/models/session.py`)
  - [x] Add language column with FK

- [x] 2.4 Update ExerciseLog model (`backend/app/models/exercise_log.py`)
  - [x] Add language column with FK
  - [x] Update __table_args__ for new unique constraint

- [x] 2.5 Update ErrorLog model (`backend/app/models/error_log.py`)
  - [x] Add language column with FK

- [x] 2.6 Update User model (`backend/app/models/user.py`)
  - [x] Add language column with FK
  - [x] Add relationship to Language (`selected_language`)

- [ ] 2.7 Update Pydantic schemas
  - [ ] Update WordCreate/WordUpdate schemas
  - [ ] Update GrammarTopicCreate schema
  - [ ] Update UserResponse/UserUpdate schemas
  - [ ] Create LanguageResponse schema

- [ ] 2.8 Add Language CRUD and API
  - [ ] Create `backend/app/crud/language.py`
  - [ ] Create `backend/app/api/languages.py`
  - [ ] Register router in `backend/app/api/router.py`

## Phase 3: CRUD Layer Updates

- [ ] 3.1 Update WordCRUD (`backend/app/crud/word.py`)
  - [ ] Add language parameter to `create()`
  - [ ] Add language filter to `get_multi()`
  - [ ] Add language filter to `count()`
  - [ ] Add language filter to `get_due_words()`
  - [ ] Add language filter to `count_due_words()`
  - [ ] Add language filter to `exists_for_user()`
  - [ ] Add language filter to `get_low_mastery_words()`
  - [ ] Add language filter to `get_random_words()`

- [ ] 3.2 Update GrammarTopicCRUD (`backend/app/crud/grammar_topic.py`)
  - [ ] Add language parameter to `create()`
  - [ ] Add language filter to `get_multi()`
  - [ ] Add language filter to `count()`
  - [ ] Add language filter to `get_by_name()`

- [ ] 3.3 Update TopicProgressCRUD (`backend/app/crud/grammar_topic.py`)
  - [ ] Update `get_user_progress()` to filter by language via join
  - [ ] Update `get_unpracticed_topics()` to filter by language
  - [ ] Update `get_learnt_topics()` to filter by language
  - [ ] Update `get_learnt_topics_with_mastery()` to filter by language

- [ ] 3.4 Update SessionCRUD (`backend/app/crud/session.py`)
  - [ ] Add language to create operations

- [ ] 3.5 Add user language methods
  - [ ] Add method to get user's selected language
  - [ ] Add method to update user's selected language

## Phase 4: API Layer Updates

- [ ] 4.1 Create language resolution dependency
  - [ ] Create `get_current_language()` dependency
  - [ ] Returns user's language

- [ ] 4.2 Update Words API (`backend/app/api/words.py`)
  - [ ] Inject language dependency
  - [ ] Pass language to CRUD methods

- [ ] 4.3 Update Drills API (`backend/app/api/drills.py`)
  - [ ] Inject language dependency
  - [ ] Pass language to service/CRUD

- [ ] 4.4 Update Exercises API (`backend/app/api/exercises.py`)
  - [ ] Inject language dependency
  - [ ] Pass language to ExerciseService

- [ ] 4.5 Update Topics API (`backend/app/api/topics.py`)
  - [ ] Inject language dependency
  - [ ] Filter topics by language

- [ ] 4.6 Update Progress API (`backend/app/api/progress.py`)
  - [ ] Inject language dependency
  - [ ] Filter progress by language

- [ ] 4.7 Update Analytics API (`backend/app/api/analytics.py`)
  - [ ] Inject language dependency
  - [ ] Filter analytics by language

- [ ] 4.8 Update Settings API (`backend/app/api/settings.py`)
  - [ ] Add GET endpoint for user's language
  - [ ] Add PATCH endpoint to change user's language

## Phase 5: Gemini Service Updates

- [ ] 5.1 Add language parameter to GeminiService
  - [ ] Update `assess_word()` signature and prompt
  - [ ] Update `assess_words_bulk()` signature and prompt
  - [ ] Update `generate_fill_in_blank()` signature and prompt
  - [ ] Update `generate_fill_in_blank_batch()` signature and prompt
  - [ ] Update `evaluate_answer()` signature and prompt

- [ ] 5.2 Update chat session prompts
  - [ ] Update system instructions to include language
  - [ ] Update exercise generation prompts

- [ ] 5.3 Update ExerciseService (`backend/app/services/exercise_service.py`)
  - [ ] Accept language parameter
  - [ ] Pass language to Gemini calls

- [ ] 5.4 Update DrillService (`backend/app/services/drill_service.py`)
  - [ ] Accept language parameter
  - [ ] Pass language to Gemini calls

## Phase 6: Frontend Language Selection

- [ ] 6.1 Add Language types (`frontend/src/types/index.ts`)
  - [ ] Add Language interface
  - [ ] Update Word interface (add language)
  - [ ] Update relevant request/response types

- [ ] 6.2 Create languageApi service
  - [ ] Create `frontend/src/services/languageApi.ts`
  - [ ] Implement `getLanguages()`
  - [ ] Implement `getUserLanguage()`
  - [ ] Implement `setUserLanguage()`

- [ ] 6.3 Create LanguageContext
  - [ ] Create `frontend/src/contexts/LanguageContext.tsx`
  - [ ] Provider with selected language state
  - [ ] Hook: `useLanguage()`

- [ ] 6.4 Update SettingsPage (`frontend/src/pages/SettingsPage.tsx`)
  - [ ] Add language selector card
  - [ ] Fetch available languages
  - [ ] Save language selection
  - [ ] Update context on change

## Phase 7: Frontend UI Updates

- [ ] 7.1 Update VocabularyPage
  - [ ] Replace hardcoded "Croatian" with context language
  - [ ] Update column headers dynamically

- [ ] 7.2 Update GrammarTopicsPage
  - [ ] Replace hardcoded "Croatian" with context language
  - [ ] Update page title/description dynamically

- [ ] 7.3 Update PracticePage
  - [ ] Replace hardcoded "Croatian" with context language
  - [ ] Update exercise descriptions

- [ ] 7.4 Update LearnPage
  - [ ] Replace hardcoded "Croatian" with context language

- [ ] 7.5 Update ProgressPage
  - [ ] Replace hardcoded "Croatian" with context language

- [ ] 7.6 Add language indicator to header/nav
  - [ ] Show current language name
  - [ ] Quick link to settings

## Phase 8: Testing & Polish

- [ ] 8.1 Seed additional test languages
  - [ ] Add Spanish, German, French
  - [ ] Via migration or admin endpoint

- [ ] 8.2 Test language switching
  - [ ] Verify vocabulary isolated per language
  - [ ] Verify grammar topics isolated per language
  - [ ] Verify progress isolated per language
  - [ ] Verify exercises generate for correct language

- [ ] 8.3 Verify existing Croatian data
  - [ ] All Croatian vocabulary accessible
  - [ ] All Croatian grammar topics accessible
  - [ ] Progress history preserved
  - [ ] Analytics work correctly

---

## Quick Reference

### Files to Create
- `backend/app/crud/language.py`
- `backend/app/api/languages.py`
- `backend/alembic/versions/xxx_add_language_to_tables.py`
- `frontend/src/services/languageApi.ts`
- `frontend/src/contexts/LanguageContext.tsx`

### Files to Modify (Backend)
- `backend/app/models/word.py`
- `backend/app/models/grammar_topic.py`
- `backend/app/models/session.py`
- `backend/app/models/exercise_log.py`
- `backend/app/models/error_log.py`
- `backend/app/models/user.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/word.py`
- `backend/app/schemas/grammar_topic.py`
- `backend/app/schemas/user.py`
- `backend/app/schemas/language.py`
- `backend/app/crud/word.py`
- `backend/app/crud/grammar_topic.py`
- `backend/app/crud/session.py`
- `backend/app/api/words.py`
- `backend/app/api/drills.py`
- `backend/app/api/exercises.py`
- `backend/app/api/topics.py`
- `backend/app/api/progress.py`
- `backend/app/api/analytics.py`
- `backend/app/api/settings.py`
- `backend/app/api/router.py`
- `backend/app/services/gemini_service.py`
- `backend/app/services/exercise_service.py`
- `backend/app/services/drill_service.py`

### Files to Modify (Frontend)
- `frontend/src/types/index.ts`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/VocabularyPage.tsx`
- `frontend/src/pages/GrammarTopicsPage.tsx`
- `frontend/src/pages/PracticePage.tsx`
- `frontend/src/pages/LearnPage.tsx`
- `frontend/src/pages/ProgressPage.tsx`
