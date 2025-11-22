# Croatian Language Tutor - Project Plan

**Last Updated: 2025-11-22**

---

## Executive Summary

Build a locally-hosted, AI-powered Croatian language learning application. The system combines **algorithmic drills** (vocabulary SRS) with **AI-powered exercises** (Gemini tutor) to get the user conversational in Croatian as quickly as possible.

**Core Principle**: Dual-mode learning - fast algorithmic drills for vocabulary, AI for conversation and complex exercises.

---

## 1. Design Decisions (COMPLETED)

### 1.1 Learning Modes

| Mode | Description | AI Required |
|------|-------------|-------------|
| **Vocabulary Drills** | SRS flashcards (CR→EN, EN→CR, fill-in-blank) | No |
| **Free Conversation** | Chat in Croatian with corrections | Yes |
| **Grammar Exercises** | Conjugation, declension drills | Yes |
| **Sentence Construction** | Build sentences from vocabulary | Yes |
| **Reading Comprehension** | Read passages, answer questions | Yes |
| **Situational Dialogues** | Role-play scenarios | Yes |
| **Sentence Translation** | CR→EN and EN→CR | Yes |

### 1.2 Vocabulary System

- **Bulk Import**: User pastes list of Croatian words → Gemini provides translations + CEFR level + ease_factor → Save to DB
- **SRS Algorithm**: SM-2 (Anki-style) for scheduling reviews
- **Drill Types**: Croatian→English, English→Croatian, Fill-in-the-blank (generated on-the-fly by Gemini)
- **Phrases**: Common short phrases stored in `word` table with `part_of_speech = 'phrase'`

### 1.3 Gemini Context Strategy

Gemini receives **on-demand computed summaries** from raw data tables:

| Summary | Content |
|---------|---------|
| Exercise Variety | Time spent per exercise type (last 7 days) |
| Topic Mastery | Completed/in-progress/not-started grammar topics with scores |
| Error Patterns | Frequent mistake categories, improving areas |
| Vocabulary Stats | Total words, by mastery level, by CEFR, due for review |
| Learning Velocity | Pace trends, progress metrics |

### 1.4 Session Handling

| Aspect | Decision |
|--------|----------|
| Within sitting | Gemini maintains conversation context |
| Across sessions | No conversation memory, only progress summaries |
| Storage | Metadata only (date, type, duration, outcome) |

### 1.5 User Model

- Single `user` table with `id=1` default
- All tables reference this user_id
- Preferences stored on user record
- Enables future multi-user extension if needed

---

## 2. Database Schema

### 2.1 Tables (Singular Names)

#### `user`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | Default: 1 |
| name | string | Optional |
| preferred_cefr_level | enum | A1-C2 |
| daily_goal_minutes | int | Target practice time |
| created_at | datetime | |
| updated_at | datetime | |

#### `word`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK | References user |
| croatian | string | Croatian word |
| english | string | Translation |
| part_of_speech | enum | noun, verb, adjective, adverb, phrase, etc. |
| gender | enum | masculine, feminine, neuter (nullable) |
| cefr_level | enum | A1-C2 (Gemini-assessed) |
| mastery_score | int | 0-10 |
| ease_factor | float | SM-2 parameter (Gemini-assessed initial) |
| correct_count | int | Successful recalls |
| wrong_count | int | Failed recalls |
| next_review_at | datetime | SRS scheduling |
| last_reviewed_at | datetime | |
| created_at | datetime | |

#### `grammar_topic`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| name | string | e.g., "Nominative Case", "Present Tense" |
| cefr_level | enum | A1-C2 |
| prerequisite_ids | int[] | Topic dependencies |
| rule_description | text | Markdown (Gemini-generated) |
| display_order | int | For UI ordering |

#### `topic_progress`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK | |
| topic_id | int FK | |
| mastery_score | int | 0-10 |
| times_practiced | int | |
| last_practiced_at | datetime | |

#### `exercise_log`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK | |
| date | date | |
| exercise_type | enum | conversation, grammar, reading, etc. |
| duration_minutes | int | |
| exercises_completed | int | |

#### `error_log`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK | |
| date | date | |
| error_category | enum | case_error, gender_agreement, verb_conjugation, word_order, spelling |
| topic_id | int FK | Nullable |
| details | text | The actual mistake |
| correction | text | Correct form |

#### `session`
| Column | Type | Notes |
|--------|------|-------|
| id | int PK | |
| user_id | int FK | |
| started_at | datetime | |
| ended_at | datetime | |
| exercise_type | enum | |
| duration_minutes | int | |
| outcome | string | Summary/result |

---

## 3. Technical Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Frontend   │───▶│   Backend    │───▶│  PostgreSQL  │      │
│  │    (React)   │    │   (FastAPI)  │    │   Database   │      │
│  │   Port 3000  │    │   Port 8000  │    │   Port 5432  │      │
│  └──────────────┘    └──────┬───────┘    └──────────────┘      │
│                             │                                   │
│                             ▼                                   │
│                    ┌──────────────┐                            │
│                    │  Gemini API  │                            │
│                    │  (External)  │                            │
│                    └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Backend Services

| Service | Responsibility |
|---------|----------------|
| `WordService` | CRUD, bulk import, SRS scheduling |
| `GeminiService` | API calls, prompt building, response parsing |
| `ExerciseService` | Exercise generation, evaluation |
| `ProgressService` | Stats computation, summary generation |
| `TopicService` | Grammar topic management |

### 3.3 Gemini Prompt Structure

```
System: You are a Croatian language tutor. Here is the student's context:

[VOCABULARY SUMMARY]
245 words total. Strong (8-10): 89, Medium (4-7): 112, Weak (0-3): 44.
By level: A1: 120, A2: 85, B1: 40. Due for review: 23 words.

[TOPIC PROGRESS]
Completed: Present Tense (9/10), Nominative Case (8/10).
In progress: Dative Case (4/10).
Not started: Instrumental Case, Past Tense.

[RECENT ACTIVITY]
Last 7 days: Reading 45min, Conversation 30min, Grammar 60min.

[ERROR PATTERNS]
Frequent: Case usage (12x, dative/locative confusion).
Improving: Verb conjugation (2 errors, down from 8).

[CURRENT TASK]
{exercise type and specific instructions}
```

---

## 4. Implementation Phases

### Phase 1: Foundation Verification ✅ COMPLETE
- ✅ Docker services start correctly (all 3 containers)
- ✅ Frontend ↔ Backend connectivity (via Docker network)
- ✅ Database connection (PostgreSQL healthy)
- ✅ Health endpoints responding
- ✅ Swagger docs accessible

### Phase 2: Database & Models ✅ COMPLETE
- ✅ SQLAlchemy models (7 tables, singular names)
- ✅ Enums (PartOfSpeech, Gender, CEFRLevel, ExerciseType, ErrorCategory)
- ✅ Alembic migration applied
- ✅ Default user seeded (id=1)
- ✅ Pydantic schemas (user, word, grammar_topic, progress, exercise)

### Phase 3: Vocabulary System (Non-AI) ← CURRENT
- Word CRUD endpoints
- Bulk import endpoint
- SRS scheduling logic
- Vocabulary drill UI

### Phase 4: Gemini Integration
- GeminiService with prompt builder
- Word assessment (CEFR, ease_factor)
- Context summary generators

### Phase 5: AI Exercises
- Exercise generation endpoints
- Evaluation endpoints
- Exercise UI components

### Phase 6: Progress & Polish
- Dashboard with stats
- Error handling
- Loading states

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gemini API rate limits | Medium | High | Cache responses, batch requests |
| Gemini response inconsistency | High | Medium | Robust parsing, fallback prompts |
| SRS algorithm edge cases | Low | Medium | Test with varied scenarios |
| Large vocabulary performance | Low | Low | Index frequently queried columns |

---

## 6. Success Metrics

- [ ] Can add vocabulary via bulk import
- [ ] Vocabulary drills work with SRS scheduling
- [ ] Can have conversation with AI tutor
- [ ] Gemini receives accurate context summaries
- [ ] Progress is tracked and visible
- [ ] All Docker services start with `docker compose up`
