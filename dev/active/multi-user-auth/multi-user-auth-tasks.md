# Multi-User Authentication - Task Checklist

**Last Updated:** 2025-11-29

---

## Phase 1: Backend Authentication Foundation

### 1.1 Dependencies & Configuration
- [ ] Add `python-jose[cryptography]>=3.3.0` to `pyproject.toml`
- [ ] Add `passlib[bcrypt]>=1.7.4` to `pyproject.toml`
- [ ] Add `python-multipart>=0.0.6` to `pyproject.toml`
- [ ] Run `pip install` / rebuild Docker container
- [ ] Add JWT settings to `backend/app/config.py`:
  - [ ] `secret_key: str`
  - [ ] `algorithm: str = "HS256"`
  - [ ] `access_token_expire_minutes: int = 30`
  - [ ] `refresh_token_expire_days: int = 7`

### 1.2 Security Core Module
- [ ] Create `backend/app/core/__init__.py`
- [ ] Create `backend/app/core/security.py` with:
  - [ ] `verify_password(plain_password, hashed_password) -> bool`
  - [ ] `get_password_hash(password) -> str`
  - [ ] `create_access_token(data: dict, expires_delta: timedelta | None) -> str`
  - [ ] `create_refresh_token(data: dict) -> str`
  - [ ] `decode_token(token: str) -> dict`

### 1.3 Auth Schemas
- [ ] Create `backend/app/schemas/auth.py` with:
  - [ ] `Token` - access_token, refresh_token, token_type
  - [ ] `TokenData` - user_id, exp
  - [ ] `UserRegister` - email, password, name (optional)
  - [ ] `UserLogin` - email, password

---

## Phase 2: Database Migration

### 2.1 User Model Updates
- [ ] Edit `backend/app/models/user.py`:
  - [ ] Add `email: Mapped[str]` (unique, indexed)
  - [ ] Add `password_hash: Mapped[str]`
  - [ ] Add `is_active: Mapped[bool]` (default=True)
  - [ ] Remove `default=1` from `id` column
  - [ ] Add `settings` relationship (one-to-one)

### 2.2 AppSettings Model Updates
- [ ] Edit `backend/app/models/app_settings.py`:
  - [ ] Remove `default=1` from `id` column
  - [ ] Add `user_id: Mapped[int]` (FK to user.id, unique)
  - [ ] Add `user` relationship

### 2.3 Schema Updates
- [ ] Edit `backend/app/schemas/user.py`:
  - [ ] Add `email` to `UserBase`
  - [ ] Add `UserCreate` schema with email, password
  - [ ] Add `email`, `is_active` to `UserResponse`

### 2.4 Alembic Migration
- [ ] Generate migration: `alembic revision --autogenerate -m "add_multi_user_auth"`
- [ ] Review generated migration for:
  - [ ] User table: add email, password_hash, is_active columns
  - [ ] AppSettings table: add user_id column
  - [ ] Proper indexes created
- [ ] Add data migration in upgrade():
  - [ ] Set existing user email='admin@local.app'
  - [ ] Set existing user password_hash=bcrypt('changeme')
  - [ ] Set existing app_settings user_id=1
- [ ] Test migration: `alembic upgrade head`
- [ ] Test rollback: `alembic downgrade -1`

---

## Phase 3: Auth API Endpoints

### 3.1 Auth Router
- [ ] Create `backend/app/api/auth.py` with:
  - [ ] `POST /auth/register` endpoint
  - [ ] `POST /auth/login` endpoint (OAuth2PasswordRequestForm)
  - [ ] `POST /auth/refresh` endpoint
  - [ ] `GET /auth/me` endpoint

### 3.2 Register Endpoint
- [ ] Validate email format
- [ ] Check email not already registered
- [ ] Hash password with bcrypt
- [ ] Create user record
- [ ] Create default AppSettings for user
- [ ] Return tokens

### 3.3 Login Endpoint
- [ ] Accept OAuth2PasswordRequestForm (username=email)
- [ ] Verify email exists
- [ ] Verify password matches hash
- [ ] Check user is_active
- [ ] Return access + refresh tokens

### 3.4 Refresh Endpoint
- [ ] Validate refresh token
- [ ] Check token not expired
- [ ] Return new access token

### 3.5 Me Endpoint
- [ ] Require valid access token
- [ ] Return current user data

### 3.6 Router Registration
- [ ] Add auth router to `backend/app/api/router.py`
- [ ] Test all endpoints via /docs

---

## Phase 4: Protected API Migration

### 4.1 Dependencies Update
- [ ] Edit `backend/app/api/dependencies.py`:
  - [ ] Add `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`
  - [ ] Add `get_current_user(token, db) -> User` dependency
  - [ ] Add `get_current_active_user(current_user) -> User` dependency
  - [ ] Update `get_current_language` to use current user
  - [ ] Remove `DEFAULT_USER_ID` constant (or keep for migration fallback)

### 4.2 User CRUD Updates
- [ ] Edit `backend/app/crud/user.py`:
  - [ ] Add `get_by_email(email: str) -> User | None`
  - [ ] Add `create(user_in: UserCreate) -> User`
  - [ ] Update `get_or_create` to not auto-create (require registration)

### 4.3 AppSettings CRUD Updates
- [ ] Edit `backend/app/crud/app_settings.py`:
  - [ ] Change `get()` signature to `get(user_id: int)`
  - [ ] Change `update()` signature to include `user_id`
  - [ ] Add `create_default(user_id: int)` for new users
  - [ ] Remove `SINGLETON_ID` constant

### 4.4 API File Updates (replace DEFAULT_USER_ID)

#### 4.4.1 Words API
- [ ] Edit `backend/app/api/words.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

#### 4.4.2 Drills API
- [ ] Edit `backend/app/api/drills.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

#### 4.4.3 Topics API
- [ ] Edit `backend/app/api/topics.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

#### 4.4.4 Exercises API
- [ ] Edit `backend/app/api/exercises.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints (many!)

#### 4.4.5 Settings API
- [ ] Edit `backend/app/api/settings.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Update `get_settings` to use `current_user.id`
  - [ ] Update `update_settings` to use `current_user.id`
  - [ ] Update language endpoints to use `current_user.id`
  - [ ] Test all endpoints

#### 4.4.6 Analytics API
- [ ] Edit `backend/app/api/analytics.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

#### 4.4.7 Progress API
- [ ] Edit `backend/app/api/progress.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

#### 4.4.8 Sessions API
- [ ] Edit `backend/app/api/sessions.py`:
  - [ ] Import `get_current_user` dependency
  - [ ] Replace all `DEFAULT_USER_ID` with `current_user.id`
  - [ ] Test all endpoints

---

## Phase 5: Frontend Authentication

### 5.1 Auth Types
- [ ] Edit `frontend/src/types/index.ts`:
  - [ ] Add `AuthToken` interface
  - [ ] Add `LoginRequest` interface
  - [ ] Add `RegisterRequest` interface
  - [ ] Add `AuthUser` interface

### 5.2 Auth API Service
- [ ] Create `frontend/src/services/authApi.ts`:
  - [ ] `login(email, password) -> AuthToken`
  - [ ] `register(email, password, name?) -> AuthToken`
  - [ ] `refresh(refreshToken) -> AuthToken`
  - [ ] `me() -> AuthUser`

### 5.3 Auth Context
- [ ] Create `frontend/src/contexts/AuthContext.tsx`:
  - [ ] State: user, tokens, isAuthenticated, isLoading
  - [ ] Actions: login, logout, register
  - [ ] Token storage in localStorage
  - [ ] Auto-refresh on mount if token exists
  - [ ] Refresh token rotation logic

### 5.4 API Interceptor
- [ ] Edit `frontend/src/services/api.ts`:
  - [ ] Add request interceptor to attach Bearer token
  - [ ] Add response interceptor for 401 handling
  - [ ] Auto-logout on invalid token

### 5.5 Protected Route Component
- [ ] Create `frontend/src/components/ProtectedRoute.tsx`:
  - [ ] Check isAuthenticated from AuthContext
  - [ ] Redirect to /login if not authenticated
  - [ ] Show loading while checking auth

### 5.6 Login Page
- [ ] Create `frontend/src/pages/LoginPage.tsx`:
  - [ ] Email input with validation
  - [ ] Password input
  - [ ] Submit button with loading state
  - [ ] Error display
  - [ ] Link to register (if implemented)
  - [ ] Redirect to / on success

### 5.7 App Routing Updates
- [ ] Edit `frontend/src/App.tsx`:
  - [ ] Wrap with AuthProvider
  - [ ] Add `/login` route (public)
  - [ ] Add `/register` route (optional, public)
  - [ ] Wrap existing routes with ProtectedRoute

### 5.8 Layout Updates
- [ ] Edit `frontend/src/components/layout/AppLayout.tsx`:
  - [ ] Add user display (email/name)
  - [ ] Add logout button
  - [ ] Connect to AuthContext

---

## Phase 6: Testing & Validation

### 6.1 Backend Tests
- [ ] Test password hashing functions
- [ ] Test JWT creation/validation
- [ ] Test register endpoint (success, duplicate email)
- [ ] Test login endpoint (success, wrong password, no user)
- [ ] Test protected endpoint without token
- [ ] Test protected endpoint with expired token
- [ ] Test protected endpoint with valid token
- [ ] Test user data isolation (user A can't see user B's data)

### 6.2 Frontend Tests
- [ ] Test login form validation
- [ ] Test successful login flow
- [ ] Test failed login error display
- [ ] Test protected route redirect
- [ ] Test logout clears tokens
- [ ] Test token persistence across refresh

### 6.3 Integration Tests
- [ ] Full flow: register -> login -> use app -> logout
- [ ] Two users with separate data
- [ ] Token expiry and refresh
- [ ] Settings isolation between users

---

## Phase 7: Documentation & Cleanup

### 7.1 Documentation
- [ ] Update CLAUDE.md with auth information
- [ ] Document new environment variables
- [ ] Update API docs in /docs endpoint
- [ ] Add login instructions to README

### 7.2 Cleanup
- [ ] Remove any remaining `DEFAULT_USER_ID` references
- [ ] Remove unused imports
- [ ] Run linter/formatter
- [ ] Review for security issues

### 7.3 Final Validation
- [ ] Fresh database migration works
- [ ] Existing data migrated correctly
- [ ] All exercises work for authenticated user
- [ ] Settings are per-user
- [ ] No data leaks between users

---

## Optional: Phase 8 (Future Enhancements)

### 8.1 Registration Improvements
- [ ] Email verification
- [ ] Password complexity validation
- [ ] CAPTCHA protection

### 8.2 Security Enhancements
- [ ] Rate limiting on auth endpoints
- [ ] Account lockout after failed attempts
- [ ] Password reset flow
- [ ] httpOnly cookies instead of localStorage

### 8.3 Admin Features
- [ ] Admin role/flag on user
- [ ] User management admin page
- [ ] Disable user accounts

---

## Progress Tracking

| Phase | Status | Est. Effort |
|-------|--------|-------------|
| Phase 1: Auth Foundation | Not Started | L |
| Phase 2: Database Migration | Not Started | M |
| Phase 3: Auth API | Not Started | M |
| Phase 4: Protected API | Not Started | XL |
| Phase 5: Frontend Auth | Not Started | L |
| Phase 6: Testing | Not Started | M |
| Phase 7: Documentation | Not Started | S |

**Total Estimated Effort:** XL (Full feature)

---

## Notes

- Phase 4 is the largest and can be parallelized (different API files can be updated independently)
- Always test endpoints after modifying them
- Keep existing functionality working during migration
- Create a test user after migration to verify everything works
