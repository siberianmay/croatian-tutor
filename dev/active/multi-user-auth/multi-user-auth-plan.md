# Multi-User Authentication Implementation Plan

**Last Updated:** 2025-11-29

---

## Executive Summary

Transform the Croatian Tutor application from a single-user local app to a multi-user system with:
1. **Password authentication** - Hashed password column on User model
2. **JWT-based login system** - Secure token authentication
3. **Per-user settings** - AppSettings tied to individual users via user_id FK
4. **Login page** - Frontend authentication flow

This is a significant architectural change affecting database schema, all API endpoints, and frontend routing.

---

## Current State Analysis

### User Model (`backend/app/models/user.py`)
- Single-user design with `id` defaulting to `1`
- No authentication fields (email, password_hash)
- Fields: `id`, `name`, `preferred_cefr_level`, `daily_goal_minutes`, `language`, `created_at`, `updated_at`
- Relationships: words, topic_progress, exercise_logs, error_logs, sessions, selected_language

### AppSettings Model (`backend/app/models/app_settings.py`)
- **Singleton pattern** - Always operates on `id=1`
- No `user_id` column - settings are global, not per-user
- Fields: `grammar_batch_size`, `translation_batch_size`, `reading_passage_length`, `gemini_model`, `updated_at`

### API Dependencies (`backend/app/api/dependencies.py`)
- **Hardcoded `DEFAULT_USER_ID = 1`** throughout entire API
- No authentication middleware
- 10 API files use `DEFAULT_USER_ID`: words, drills, topics, exercises, settings, analytics, progress, sessions

### Frontend State
- No authentication context or routing guards
- No login/register pages
- Direct API access without tokens
- Settings page displays global settings

---

## Proposed Future State

### Database Schema Changes

**User Model Additions:**
```python
email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

**AppSettings Model Changes:**
```python
# Remove singleton pattern
id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, unique=True)

# Add relationship
user: Mapped["User"] = relationship(back_populates="settings")
```

**User Model Relationship Addition:**
```python
settings: Mapped["AppSettings"] = relationship(back_populates="user", uselist=False)
```

### Authentication System

**New Dependencies (pyproject.toml):**
- `python-jose[cryptography]>=3.3.0` - JWT encoding/decoding
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-multipart>=0.0.6` - Form data parsing (login form)

**New Files:**
- `backend/app/core/security.py` - Password hashing, JWT creation/verification
- `backend/app/api/auth.py` - Login, register, refresh token endpoints
- `backend/app/api/dependencies.py` - `get_current_user` dependency (replace `DEFAULT_USER_ID`)

**Config Additions:**
```python
# JWT Settings
secret_key: str = "your-secret-key-change-in-production"
algorithm: str = "HS256"
access_token_expire_minutes: int = 30
```

### API Changes

**All endpoints using `DEFAULT_USER_ID` must:**
1. Accept JWT token via `Authorization: Bearer <token>` header
2. Use `get_current_user` dependency to extract `user_id`
3. Filter all queries by `user_id`

**Files requiring modification:**
- `backend/app/api/words.py`
- `backend/app/api/drills.py`
- `backend/app/api/topics.py`
- `backend/app/api/exercises.py`
- `backend/app/api/settings.py`
- `backend/app/api/analytics.py`
- `backend/app/api/progress.py`
- `backend/app/api/sessions.py`
- `backend/app/api/dependencies.py`

### Frontend Changes

**New Files:**
- `frontend/src/contexts/AuthContext.tsx` - Auth state management
- `frontend/src/pages/LoginPage.tsx` - Login form
- `frontend/src/pages/RegisterPage.tsx` - Registration form (optional, Phase 2)
- `frontend/src/services/authApi.ts` - Auth API calls
- `frontend/src/components/ProtectedRoute.tsx` - Route guard

**Modified Files:**
- `frontend/src/App.tsx` - Add auth routes, protect existing routes
- `frontend/src/services/api.ts` - Add JWT interceptor
- `frontend/src/types/index.ts` - Add auth types

---

## Implementation Phases

### Phase 1: Backend Authentication Foundation (Effort: L)
**Goal:** Set up password hashing and JWT infrastructure

1. Add dependencies to `pyproject.toml`
2. Create `backend/app/core/security.py`
3. Add JWT config to `backend/app/config.py`
4. Create User schema extensions for registration/login

### Phase 2: Database Migration (Effort: M)
**Goal:** Update User and AppSettings models

1. Add `email`, `password_hash`, `is_active` to User model
2. Add `user_id` FK to AppSettings model
3. Create Alembic migration
4. Update seed scripts if any

### Phase 3: Auth API Endpoints (Effort: M)
**Goal:** Implement login/register/refresh endpoints

1. Create `backend/app/api/auth.py` with:
   - `POST /auth/register` - Create new user
   - `POST /auth/login` - Return JWT token
   - `POST /auth/refresh` - Refresh expired token
   - `GET /auth/me` - Get current user info
2. Add router to `backend/app/api/router.py`

### Phase 4: Protected API Migration (Effort: XL)
**Goal:** Replace `DEFAULT_USER_ID` with authenticated user

1. Create `get_current_user` dependency in `dependencies.py`
2. Update all 8 API files to use `Depends(get_current_user)`
3. Update CRUD operations to filter by `user_id`
4. Update AppSettings CRUD to use `user_id` instead of singleton

### Phase 5: Frontend Authentication (Effort: L)
**Goal:** Implement login flow and protected routes

1. Create `AuthContext` with login/logout/token state
2. Create `LoginPage` component
3. Add JWT interceptor to axios instance
4. Wrap app routes in `ProtectedRoute`
5. Add logout button to AppLayout

### Phase 6: Settings Migration (Effort: S)
**Goal:** Make settings per-user

1. Update `AppSettingsCRUD` to query by `user_id`
2. Update `settings.py` API to use current user
3. Auto-create default settings on user registration
4. Update frontend settings page (minimal changes)

---

## Risk Assessment and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing data | High | Medium | Create data migration script for existing user |
| Token security vulnerabilities | High | Low | Use industry-standard libraries (python-jose, passlib) |
| Session management complexity | Medium | Medium | Keep JWT stateless, short expiry with refresh |
| Frontend routing issues | Medium | Low | Test all routes with/without auth |
| Performance degradation | Low | Low | JWT validation is fast, no DB hit |

### Data Migration Strategy
For existing single-user data:
1. Migration adds columns with defaults
2. Existing user gets `email=admin@local.app`, `password_hash=<bcrypt hash of 'changeme'>`
3. Existing AppSettings row gets `user_id=1`
4. Document that user should change password on first login

---

## Success Metrics

1. **Functional:** Multiple users can register, login, and have isolated data
2. **Security:** Passwords properly hashed, JWTs expire correctly
3. **Performance:** Login < 200ms, API calls unchanged latency
4. **UX:** Smooth login flow, clear error messages
5. **Data Integrity:** Existing user data preserved and accessible

---

## Required Dependencies

### Backend (pyproject.toml additions)
```toml
"python-jose[cryptography]>=3.3.0",
"passlib[bcrypt]>=1.7.4",
"python-multipart>=0.0.6",
```

### Frontend (no new dependencies needed)
- React Query already handles API state
- Axios already supports interceptors

---

## Technical Decisions

### JWT vs Session Cookies
**Decision:** JWT with Bearer token
**Rationale:**
- Stateless, no server-side session storage needed
- Works well with SPA architecture
- Standard FastAPI pattern

### Password Hashing Algorithm
**Decision:** bcrypt via passlib
**Rationale:**
- Industry standard, resistant to rainbow tables
- Built-in salt handling
- Configurable work factor

### Token Storage (Frontend)
**Decision:** localStorage with short expiry + refresh token
**Rationale:**
- Simple implementation
- Refresh token allows longer sessions without security risk
- Can upgrade to httpOnly cookies later if needed

### AppSettings Relationship
**Decision:** One-to-one with User (unique constraint on user_id)
**Rationale:**
- Each user has exactly one settings record
- Auto-created on registration
- Simpler than nullable user_id with singleton fallback

---

## API Endpoint Summary

### New Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create new user account |
| POST | /auth/login | Authenticate and get JWT |
| POST | /auth/refresh | Get new JWT using refresh token |
| GET | /auth/me | Get current user details |

### Modified Endpoints (all require Bearer token)
All existing endpoints under `/api/v1/` will require authentication and use the token's user_id instead of hardcoded `DEFAULT_USER_ID`.

---

## File Change Summary

### New Files
- `backend/app/core/__init__.py`
- `backend/app/core/security.py`
- `backend/app/api/auth.py`
- `backend/app/schemas/auth.py`
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/services/authApi.ts`
- `frontend/src/components/ProtectedRoute.tsx`

### Modified Files
- `backend/pyproject.toml` - Add dependencies
- `backend/app/config.py` - Add JWT settings
- `backend/app/models/user.py` - Add auth fields
- `backend/app/models/app_settings.py` - Add user_id FK
- `backend/app/schemas/user.py` - Add auth schemas
- `backend/app/crud/user.py` - Add email lookup
- `backend/app/crud/app_settings.py` - Query by user_id
- `backend/app/api/dependencies.py` - Add get_current_user
- `backend/app/api/router.py` - Add auth router
- `backend/app/api/settings.py` - Use current user
- `backend/app/api/words.py` - Use current user
- `backend/app/api/drills.py` - Use current user
- `backend/app/api/topics.py` - Use current user
- `backend/app/api/exercises.py` - Use current user
- `backend/app/api/analytics.py` - Use current user
- `backend/app/api/progress.py` - Use current user
- `backend/app/api/sessions.py` - Use current user
- `frontend/src/App.tsx` - Add auth routes
- `frontend/src/services/api.ts` - Add JWT interceptor
- `frontend/src/types/index.ts` - Add auth types
- `frontend/src/components/layout/AppLayout.tsx` - Add logout

### New Migration
- `backend/alembic/versions/xxx_add_multi_user_auth.py`
