# Multi-User Authentication - Context Document

**Last Updated:** 2025-11-29

---

## Key Files Reference

### Backend - Models
| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/models/user.py` | User model, needs email/password_hash | ~63 |
| `backend/app/models/app_settings.py` | AppSettings, needs user_id FK | ~59 |
| `backend/app/models/__init__.py` | Model exports | - |

### Backend - Schemas
| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/schemas/user.py` | User Pydantic schemas | ~36 |
| `backend/app/schemas/app_settings.py` | AppSettings schemas | ~70 |

### Backend - CRUD
| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/crud/user.py` | User CRUD operations | ~57 |
| `backend/app/crud/app_settings.py` | AppSettings CRUD (singleton pattern) | ~60 |

### Backend - API Routes (use DEFAULT_USER_ID)
| File | Endpoints | Impact |
|------|-----------|--------|
| `backend/app/api/dependencies.py` | `get_current_language`, `DEFAULT_USER_ID=1` | **Primary change point** |
| `backend/app/api/words.py` | Word CRUD endpoints | High - many endpoints |
| `backend/app/api/drills.py` | Drill session endpoints | Medium |
| `backend/app/api/topics.py` | Grammar topics | Medium |
| `backend/app/api/exercises.py` | All exercise types | High - most complex |
| `backend/app/api/settings.py` | AppSettings + language | Medium |
| `backend/app/api/analytics.py` | Analytics dashboard | Medium |
| `backend/app/api/progress.py` | Progress tracking | Medium |
| `backend/app/api/sessions.py` | Session management | Medium |

### Backend - Configuration
| File | Purpose |
|------|---------|
| `backend/app/config.py` | Pydantic Settings (add JWT config) |
| `backend/app/main.py` | FastAPI app setup |
| `backend/pyproject.toml` | Dependencies (add auth libs) |

### Frontend - Core
| File | Purpose |
|------|---------|
| `frontend/src/App.tsx` | Routes (add login, protect routes) |
| `frontend/src/main.tsx` | App entry point |
| `frontend/src/services/api.ts` | Axios instance (add JWT interceptor) |
| `frontend/src/types/index.ts` | TypeScript types (add auth types) |

### Frontend - Services
| File | Purpose |
|------|---------|
| `frontend/src/services/settingsApi.ts` | Settings API calls |
| `frontend/src/services/wordApi.ts` | Word API calls |
| `frontend/src/services/exerciseApi.ts` | Exercise API calls |

### Frontend - Pages
| File | Purpose |
|------|---------|
| `frontend/src/pages/SettingsPage.tsx` | Settings UI |
| `frontend/src/components/layout/AppLayout.tsx` | Main layout (add logout) |

---

## Dependencies to Add

### Backend (pyproject.toml)
```toml
dependencies = [
    # ... existing ...
    "python-jose[cryptography]>=3.3.0",  # JWT
    "passlib[bcrypt]>=1.7.4",             # Password hashing
    "python-multipart>=0.0.6",            # Form data
]
```

### Frontend
No new dependencies - existing stack sufficient:
- `@tanstack/react-query` - API state
- `axios` - HTTP client with interceptors
- `react-router-dom` - Routing/guards

---

## Critical Code Patterns

### Current: Hardcoded User ID
```python
# backend/app/api/dependencies.py
DEFAULT_USER_ID = 1

async def get_current_language(
    user_crud: Annotated[UserCRUD, Depends(get_user_crud)],
) -> str:
    return await user_crud.get_language(DEFAULT_USER_ID)
```

### Target: JWT-Based User
```python
# backend/app/api/dependencies.py
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserCRUD(db).get(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Current: Singleton AppSettings
```python
# backend/app/crud/app_settings.py
class AppSettingsCRUD:
    SINGLETON_ID = 1

    async def get(self) -> AppSettings:
        result = await self._db.execute(
            select(AppSettings).where(AppSettings.id == self.SINGLETON_ID)
        )
```

### Target: Per-User AppSettings
```python
# backend/app/crud/app_settings.py
class AppSettingsCRUD:
    async def get(self, user_id: int) -> AppSettings:
        result = await self._db.execute(
            select(AppSettings).where(AppSettings.user_id == user_id)
        )
```

---

## Database Schema Changes

### User Table - Before
```sql
CREATE TABLE "user" (
    id INTEGER PRIMARY KEY DEFAULT 1,
    name VARCHAR(100),
    preferred_cefr_level VARCHAR(2) NOT NULL DEFAULT 'A1',
    daily_goal_minutes INTEGER NOT NULL DEFAULT 30,
    language VARCHAR(8) NOT NULL DEFAULT 'hr',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### User Table - After
```sql
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,  -- Remove default=1
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    name VARCHAR(100),
    preferred_cefr_level VARCHAR(2) NOT NULL DEFAULT 'A1',
    daily_goal_minutes INTEGER NOT NULL DEFAULT 30,
    language VARCHAR(8) NOT NULL DEFAULT 'hr',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_user_email ON "user" (email);
```

### AppSettings Table - Before
```sql
CREATE TABLE app_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    grammar_batch_size INTEGER NOT NULL DEFAULT 10,
    translation_batch_size INTEGER NOT NULL DEFAULT 10,
    reading_passage_length INTEGER NOT NULL DEFAULT 350,
    gemini_model VARCHAR(50) NOT NULL DEFAULT 'gemini-2.5-flash',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### AppSettings Table - After
```sql
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    grammar_batch_size INTEGER NOT NULL DEFAULT 10,
    translation_batch_size INTEGER NOT NULL DEFAULT 10,
    reading_passage_length INTEGER NOT NULL DEFAULT 350,
    gemini_model VARCHAR(50) NOT NULL DEFAULT 'gemini-2.5-flash',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX ix_app_settings_user_id ON app_settings (user_id);
```

---

## Session Progress

### Current Session
- [x] Analyzed User model structure
- [x] Analyzed AppSettings singleton pattern
- [x] Identified all API files using DEFAULT_USER_ID (10 files)
- [x] Reviewed frontend auth requirements
- [x] Created comprehensive plan
- [ ] Implementation not started

### Blockers
None identified.

### Decisions Made
1. **JWT over session cookies** - Stateless, SPA-friendly
2. **bcrypt via passlib** - Industry standard password hashing
3. **One-to-one User-AppSettings** - Unique constraint on user_id
4. **Short-lived access + refresh token** - Security best practice

### Open Questions
1. Should registration be open or admin-only initially?
   - **Suggested:** Open registration for MVP, can add approval workflow later
2. Password complexity requirements?
   - **Suggested:** Min 8 chars for MVP, can enhance later
3. Token expiry duration?
   - **Suggested:** Access: 30min, Refresh: 7 days

---

## Related Existing Features

### Language Selection (Already Per-User)
The `language` field on User already provides per-user language selection.
No changes needed - this pattern should be followed for other features.

### Word/Progress Data (Already User-Scoped)
Word model has `user_id` foreign key.
TopicProgress has `user_id` foreign key.
These are already designed for multi-user but currently always use `DEFAULT_USER_ID`.

---

## Migration Considerations

### Existing Data Handling
1. **Existing User (id=1):**
   - Set `email='admin@local.app'`
   - Set `password_hash=<bcrypt hash of 'changeme'>`
   - Set `is_active=True`
   - Log warning to change password

2. **Existing AppSettings (id=1):**
   - Set `user_id=1` to link to existing user

3. **All Other Tables:**
   - No changes needed - already have `user_id` FK where appropriate

### Rollback Plan
1. Keep migration reversible (Alembic downgrade)
2. Remove new columns: `email`, `password_hash`, `is_active` from User
3. Remove `user_id` from AppSettings
4. Restore `DEFAULT_USER_ID` constant in dependencies

---

## Testing Strategy

### Backend Tests Needed
- [ ] Password hashing/verification
- [ ] JWT creation/validation
- [ ] Token expiry handling
- [ ] Login endpoint (success/failure)
- [ ] Register endpoint (success/duplicate email)
- [ ] Protected endpoint without token (401)
- [ ] Protected endpoint with valid token (200)
- [ ] AppSettings per-user isolation

### Frontend Tests Needed
- [ ] Login form validation
- [ ] Login success redirect
- [ ] Token storage/retrieval
- [ ] Protected route redirect to login
- [ ] Logout clears state
- [ ] API calls include token

---

## References

### FastAPI Security Docs
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

### Passlib bcrypt
https://passlib.readthedocs.io/en/stable/lib/passlib.hash.bcrypt.html

### python-jose
https://python-jose.readthedocs.io/en/latest/
