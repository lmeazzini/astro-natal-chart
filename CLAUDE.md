# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **natal chart (birth chart) generation system** using traditional astrology. The application provides astronomical calculations (Swiss Ephemeris), professional chart visualization, and basic astrological interpretations. The project is LGPD/GDPR compliant and handles sensitive personal data (birth date/time/location).

**Current Status**: MVP in progress (~78% complete). Core functionality is working: authentication, chart creation, calculations, and visualization. Email verification, password reset, and rate limiting implemented.

**Tech Stack:**
- **Monorepo**: Turborepo (npm workspaces)
- **Backend**: Python 3.11+ with FastAPI (async), PostgreSQL 16 (JSONB), Redis
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Astrology Engine**: PySwisseph (Moshier ephemeris - built-in)
- **Infrastructure**: Docker Compose for development

## Essential Commands

### Quick Start (Docker - Recommended)
```bash
# Setup environment files first
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

# Start all services (db, redis, api, celery_worker, web)
make docker-up

# Run database migrations
make migrate

# View logs
make docker-logs
```

### Development Without Docker
```bash
# Install all dependencies (monorepo + backend + frontend)
make install

# Start development servers (Turborepo parallel execution)
make dev

# Or manually:
# Backend: cd apps/api && uvicorn app.main:app --reload
# Frontend: cd apps/web && npm run dev
```

### Package Management (UV)

The backend uses **UV** (https://github.com/astral-sh/uv) - a blazing-fast Python package manager written in Rust (10-100x faster than pip).

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies from pyproject.toml (production + dev)
cd apps/api && uv sync

# Install only production dependencies
cd apps/api && uv sync --no-dev

# Add a new dependency
cd apps/api && uv add package-name

# Add a dev dependency
cd apps/api && uv add --dev package-name

# Update dependencies
cd apps/api && uv lock --upgrade

# Run commands in UV-managed environment
cd apps/api && uv run pytest
cd apps/api && uv run mypy app/

# Create/update uv.lock from pyproject.toml
cd apps/api && uv lock
```

**Key files:**
- `pyproject.toml`: Project metadata and dependencies (PEP 621 standard)
- `uv.lock`: Lockfile with exact versions (similar to package-lock.json)
- `requirements.txt`: Legacy file, kept for compatibility but UV uses pyproject.toml

**Note**: Docker build now uses UV instead of pip for faster builds.

### Testing
```bash
# All tests (backend + frontend)
make test

# Backend only (pytest with coverage)
cd apps/api && pytest --cov=app --cov-report=html

# Frontend only (vitest)
cd apps/web && npm run test

# Single test file
cd apps/api && pytest tests/test_astro/test_calculator.py -v

# Single test function
cd apps/api && pytest tests/test_api/test_auth.py::test_register_user -v
```

**NOTE**: Test infrastructure exists but no tests are written yet (0% coverage). Test directories exist at `apps/api/tests/` and frontend test setup is configured.

### Database Migrations (Alembic)
```bash
# Run migrations
make migrate

# Create new migration (autogenerate from models)
make migrate-create
# Or: cd apps/api && alembic revision --autogenerate -m "description"

# Rollback last migration
make migrate-down

# Reset database (destroys all data)
make db-reset
```

### Code Quality
```bash
# Lint all code (backend Ruff + frontend ESLint)
make lint

# Format all code (backend Ruff + frontend Prettier)
make format

# Backend type checking
cd apps/api && mypy app/

# Frontend type checking
cd apps/web && npm run type-check
```

### CI Verification (MANDATORY Before Commit)

**ALWAYS run these checks locally before committing** to ensure CI will pass:

```bash
# Quick verification (runs all CI checks locally)
make lint                    # Backend + Frontend linting
cd apps/api && uv run mypy app/    # Backend type checking
cd apps/web && npm run type-check  # Frontend type checking
cd apps/web && npm run build       # Verify frontend builds

# Alternative: Run individual checks
cd apps/api && uv run ruff check .    # Backend linting (Ruff)
cd apps/web && npm run lint           # Frontend linting (ESLint)
```

**Why this matters:**
- The CI pipeline runs the EXACT same checks
- If any check fails locally, it WILL fail in CI
- Failed CI blocks merging and wastes time
- Mypy and Ruff have **zero tolerance** for errors

**CI Pipeline Jobs:**
1. **Backend**: Ruff linting + Mypy type checking
2. **Frontend**: ESLint + TypeScript type checking
3. **Build**: Vite production build

All 3 jobs must be GREEN before merging.

### Docker Management
```bash
make docker-up          # Start services
make docker-down        # Stop services
make docker-restart     # Restart services
make docker-rebuild     # Rebuild images and restart
make docker-logs        # View all logs
make api-logs           # View API logs only
make web-logs           # View frontend logs only
make api-shell          # Python shell in API container
make web-shell          # Shell in web container
```

## Architecture & Critical Patterns

### Monorepo Structure
```
apps/
  api/           # Python FastAPI backend
  web/           # React TypeScript frontend
packages/        # Shared code (EMPTY - planned for future)
```

All apps are orchestrated by **Turborepo** (`turbo.json`). Running `npm run dev` from root executes both frontend and backend in parallel.

**IMPORTANT**: The `packages/shared-types/` and `packages/ui-components/` directories exist but are empty placeholders for future work.

### Backend Architecture (FastAPI)

**Layered architecture:**
1. **API Layer** (`app/api/v1/endpoints/`): FastAPI routes, request/response handling
2. **Service Layer** (`app/services/`): Business logic orchestration
3. **Repository Layer** (`app/repositories/`): Data access abstraction
4. **Data Layer** (`app/models/`): SQLAlchemy models, database schema

**Key patterns:**
- **Async everywhere**: SQLAlchemy async engine, FastAPI async endpoints
- **Dependency Injection**: FastAPI's `Depends()` for `get_db()` and `get_current_user()`
- **Repository pattern**: Data access abstracted through repository layer
  - `BaseRepository`: Generic CRUD operations
  - `UserRepository`: User-specific queries (by email, active users, etc.)
  - `OAuthAccountRepository`: OAuth account queries
  - `ChartRepository`: Chart queries with authorization (by user, soft delete, search, tags)
  - `AuditRepository`: Audit log creation and queries

**Database (PostgreSQL with JSONB):**
- User accounts and OAuth providers in normalized tables
- Birth chart **metadata** in columns (name, birth_datetime, lat/lon, etc.)
- Birth chart **calculated data** in `chart_data` JSONB column for flexibility
  - Structure: `{"planets": [...], "houses": [...], "aspects": [...], "chart_info": {...}}`
- Soft deletes via `deleted_at` timestamp
- Audit logs for LGPD/GDPR compliance

**Critical models:**
- `User`: email, password_hash, relationships to birth_charts and oauth_accounts
- `BirthChart`: person_name, birth_datetime (TZ-aware), lat/lon, chart_data (JSONB)
- `OAuthAccount`: Links external OAuth providers to users
- `AuditLog`: Tracks sensitive actions (login, chart creation, deletion)

**Authentication flow:**
- JWT tokens (access: 15 min, refresh: 30 days)
- Access token in Authorization header, refresh token in HTTP-only cookie
- `get_current_user()` dependency validates JWT and fetches user from DB
- OAuth2 flow creates/links local user accounts

### Frontend Architecture (React)

**Structure:**
- `src/pages/`: Route components (Login, Register, ChartDetail, NewChart, Charts, Dashboard)
- `src/components/`: Reusable UI components (ChartWheel, PlanetList, AspectGrid, HouseTable)
- `src/services/`: API client (fetch-based, NOT axios despite being installed)
- `src/contexts/`: AuthContext for authentication state
- `src/utils/`: Utility functions (astro symbols, cn for className merging)

**IMPORTANT State Management Reality:**
- **Actually using**: React Context API for auth, component state for everything else
- **Installed but NOT used**: React Query (@tanstack/react-query), Zustand
- **Form handling**: Controlled inputs with useState (React Hook Form and Zod are installed but not actively used)

**API communication:**
- Fetch API in `src/services/` (axios is installed but not used)
- JWT from localStorage added to Authorization header
- Manual error handling (no response interceptors)

### Astrological Calculations (Critical Domain Logic)

**ACTUAL IMPLEMENTATION**: All calculation logic is in `apps/api/app/services/astro_service.py` (374 lines)

**The `apps/api/app/astro/` directory exists but is EMPTY** - this was planned for future refactoring but currently all logic is in the service layer.

**Actually Implemented:**
- ✅ PySwisseph integration with **Moshier ephemeris** (built-in, no external files needed)
- ✅ Julian Day conversion with timezone support (via timezonefinder)
- ✅ Planet positions: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, North Node
- ✅ House systems: Placidus (default), Koch, Equal, Whole Sign, Campanus, Regiomontanus
- ✅ House cusp calculations (all 12 houses + ASC/MC/IC/DC)
- ✅ Aspect detection: Conjunction (0°), Opposition (180°), Trine (120°), Square (90°), Sextile (60°), Quincunx (150°), Semisextile (30°), Semisquare (45°), Sesquiquadrate (135°)
- ✅ Configurable aspect orbs (default: 8° for major, 3° for minor)
- ✅ Applying/separating aspect detection (based on planet speeds)
- ✅ Retrograde detection
- ✅ Sign and degree calculations (e.g., "15° Taurus")

**NOT Implemented (requires external ephemeris files or additional logic):**
- ❌ Chiron and asteroids (Ceres, Pallas, Juno, Vesta)
- ❌ Essential dignities calculation (rulership, exaltation, triplicity, term, face)
- ❌ Sect determination (day/night chart)
- ❌ Lot of Fortune calculation
- ❌ Text interpretations (no template engine)
- ❌ Fixed stars conjunctions
- ❌ High-precision JPL DE431 ephemeris (currently using lower-precision Moshier)

**Precision:**
- Current: Moshier ephemeris (good for most uses, ~1-2 arcsecond error)
- Target: JPL DE431 (< 0.001° error, requires external ephemeris files)

**Chart data structure (stored in BirthChart.chart_data JSONB):**
```json
{
  "planets": [
    {
      "name": "Sun",
      "longitude": 45.123,
      "latitude": 0.002,
      "speed": 0.985,
      "retrograde": false,
      "sign": "Taurus",
      "degree": 15.123,
      "house": 10
    }
  ],
  "houses": [
    {"number": 1, "cusp": 123.456, "sign": "Leo"}
  ],
  "aspects": [
    {
      "planet1": "Sun",
      "planet2": "Moon",
      "aspect": "trine",
      "angle": 120.0,
      "orb": 2.3,
      "applying": true
    }
  ],
  "chart_info": {
    "ascendant": 123.456,
    "mc": 234.567,
    "ic": 303.456,
    "descendant": 303.456
  }
}
```

### Celery Async Tasks

**Location:** `apps/api/app/tasks/`

**CURRENT STATUS**: Privacy tasks implemented in `app/tasks/privacy.py`

**Implemented tasks:**
- ✅ `cleanup_deleted_users()`: Hard delete users after 30-day retention period (LGPD compliance)
  - Runs daily at 3 AM
  - Removes all user data (charts, OAuth accounts, consents, tokens)
  - Keeps audit logs for 5 years (legal requirement)

**Planned use cases:**
- PDF generation (heavy LaTeX compilation)
- Bulk chart calculations
- Email sending (future)

**Setup:**
- Celery worker runs in separate Docker container
- Redis as message broker and result backend
- Scheduled via Celery Beat (periodic tasks)

### Environment Configuration

**Backend** (`apps/api/.env`):
- `DATABASE_URL`: PostgreSQL async URL (postgresql+asyncpg://...)
- `SECRET_KEY`: For JWT signing (CRITICAL - change in production)
- OAuth2 credentials: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, `FACEBOOK_CLIENT_ID` + secrets
- `OPENCAGE_API_KEY`: For geocoding (location search)
- `OPENAI_API_KEY`: For AI interpretations (optional, sk-proj-...)
- `SMTP_*`: Gmail SMTP for emails (optional, see issue #40 for setup)
- `ALLOWED_ORIGINS`: CORS configuration

**Frontend** (`apps/web/.env`):
- `VITE_API_URL`: Backend API URL (http://localhost:8000 in dev)
- `VITE_GOOGLE_CLIENT_ID`: For Google OAuth button

## Critical Development Patterns

### Adding New Repository

1. Create repository class in `app/repositories/` (inherit from `BaseRepository`)
2. Add specialized query methods for the model
3. Import and use in service layer

Example:
```python
# app/repositories/my_repository.py
from app.repositories.base import BaseRepository
from app.models.my_model import MyModel

class MyRepository(BaseRepository[MyModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(MyModel, db)

    async def get_by_custom_field(self, value: str) -> MyModel | None:
        stmt = select(MyModel).where(MyModel.custom_field == value)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
```

### Adding New API Endpoint

1. Create Pydantic schemas in `app/schemas/` (request/response)
2. Create repository in `app/repositories/` (if new model)
3. Add business logic in `app/services/` (use repository)
4. Create route in `app/api/v1/endpoints/`
5. Use `Depends(get_current_user)` for authenticated endpoints
6. Document with FastAPI docstrings (auto-generates OpenAPI)

Example:
```python
# app/services/my_service.py
from app.repositories.my_repository import MyRepository

async def create_item(db: AsyncSession, data: ItemCreate) -> Item:
    repo = MyRepository(db)
    item = Item(**data.model_dump())
    return await repo.create(item)

# app/api/v1/endpoints/items.py
@router.post("/", response_model=ItemRead, status_code=201)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await my_service.create_item(db, item_data)
```

### Adding Database Model

1. Create model in `app/models/` (inherit from `Base`)
2. Import model in `alembic/env.py` (for autogenerate to detect it)
3. Create migration: `make migrate-create`
4. Review generated migration in `alembic/versions/`
5. Apply: `make migrate`

**Critical:** Always use UUID primary keys (`uuid4()`) and timezone-aware datetimes.

### Adding React Component

1. Create in `src/components/` or `src/pages/`
2. Use TypeScript with explicit prop types
3. Use Tailwind for styling
4. Use `cn()` utility from `@/utils/cn` for conditional classes
5. For forms, use controlled inputs with useState (React Hook Form is available but not currently in use)

### API Call Pattern

Currently using **plain fetch API** (NOT React Query):
```typescript
// src/services/charts.ts
export async function createChart(chartData: ChartCreate): Promise<Chart> {
  const response = await fetch(`${API_URL}/api/v1/charts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(chartData),
  });

  if (!response.ok) throw new Error('Failed to create chart');
  return response.json();
}
```

**NOTE**: React Query is installed but not currently integrated. If you want to use it, you'll need to add QueryClientProvider to App.tsx and convert service calls to use `useQuery`/`useMutation`.

## Security & Compliance

- **NEVER** commit `.env` files or secrets
- **Password hashing:** bcrypt with cost factor 12
- **Sensitive data:** Birth date/time/location are personal data (LGPD/GDPR)
- **Audit logging:** Log all chart creations, deletions, user logins (implemented)
- **Soft deletes:** `deleted_at` timestamp, hard delete after 30 days (Celery task)
- **CORS:** Configured in backend (`ALLOWED_ORIGINS`)
- **Rate limiting:** ✅ IMPLEMENTED (SlowAPI + Redis)
  - Configured in `app/core/rate_limit.py`
  - Applied to all critical endpoints (auth, charts, password reset, geocoding)
  - Can be disabled for testing via `RATE_LIMIT_ENABLED=false`

## Testing Guidelines

**CURRENT STATUS**: ~30% backend coverage, 0% frontend coverage

**Backend testing (pytest):**
- `apps/api/tests/test_api/` - API endpoint tests
  - ✅ `test_auth.py` - 24 tests (register, login, refresh, logout, email verification)
  - TestRegister: 6 tests
  - TestLogin: 5 tests
  - TestRefreshToken: 4 tests
  - TestGetCurrentUser: 4 tests
  - TestLogout: 3 tests
  - TestAuthenticationFlow: 2 tests
- `apps/api/tests/test_astro/` - Calculation tests (empty - needs implementation)
- `apps/api/tests/test_services/` - Service tests (empty - needs implementation)

**Test configuration:**
- Fixtures: `db_session`, `client`, `test_user`, `test_user_factory`, `test_chart_factory`
- PostgreSQL + Redis in CI (GitHub Actions)
- Rate limiting disabled in tests via `RATE_LIMIT_ENABLED=false` (set in conftest.py before imports)
- Transaction rollback for fast test isolation

**Frontend testing:**
- Vitest configured in `package.json`
- @testing-library/react installed
- No test files written yet (~0% coverage)

**When writing tests:**
- Backend: Use pytest fixtures for DB setup (transaction rollback)
- Astrological calculations: Validate against known cases (compare with astro.com)
- Frontend: Use Testing Library, avoid implementation details
- Coverage target: 70% minimum backend, 60% minimum frontend

## Docker Services

When running `docker-compose up -d`, these services start:

1. **db** (postgres:16-alpine) - Port 5432
2. **redis** (redis:7-alpine) - Port 6379
3. **api** (FastAPI) - Port 8000, depends on db+redis
4. **celery_worker** (Celery) - No exposed port, depends on db+redis (NOT USED YET)
5. **web** (React+Vite) - Port 5173, depends on api

All services are on `astro-network` bridge network with persistent volumes for postgres and redis data.

## Logging System

**Library:** Loguru (replaces standard Python logging)

**Configuration:** `apps/api/app/core/logging_config.py`

**Features:**
- **Development**: Colorized console logs with DEBUG level
- **Production**: JSON structured logs with rotation (500 MB, 30 days retention, compressed)
- **Request tracking**: Unique request_id per request via middleware
- **Context binding**: Can add user_id, request_id to all logs

**Usage:**
```python
from loguru import logger

# Simple logging
logger.info("Starting calculation")
logger.error(f"Failed to process: {error}")

# With context
logger.bind(user_id=user.id).info("Chart created")
```

**Request middleware:** `apps/api/app/core/middleware.py`
- Adds X-Request-ID header to responses
- Logs incoming requests and completion time
- Automatically binds request_id to all logs in request scope

## Docker Watchfiles Fix

**Issue:** Uvicorn's file watcher crashes in Docker/WSL2 when watching `.venv/` directory.

**Solution (already implemented):**
- Added `--reload-exclude '.venv/*'` to uvicorn command in docker-compose.yml
- Added anonymous volume `/app/.venv` to prevent .venv from being watched
- This is critical for Docker stability - do not remove these configurations

## Common Pitfalls

1. **Alembic migrations not detected:** Ensure model is imported in `alembic/env.py`
2. **Async/sync mismatch:** Backend is fully async - use `async def` and `await`
3. **JSONB queries:** Use PostgreSQL JSONB operators (`->`, `->>`, `@>`) for querying chart_data
4. **Timezone handling:** Always use timezone-aware datetimes, store birth_timezone IANA name
5. **PySwisseph precision:** Currently using Moshier (built-in). For high precision, need to download ephemeris files and set `EPHEMERIS_PATH`
6. **Empty directories:** `packages/`, `app/astro/` exist but are empty/unused
7. **Installed but unused:** React Query, Zustand, axios, React Hook Form (installed but not actively used in current code)
8. **Docker watchfiles:** Never remove `.venv` exclusions from docker-compose.yml - causes container crashes

## What's Actually Working vs. Planned

**✅ WORKING:**
- User registration and login (JWT + OAuth2: Google, GitHub, Facebook)
- **Email verification** (JWT tokens, 24h expiration, automatic on registration)
- **Password reset** (SHA256 tokens, 1h expiration, email with reset link)
- **Rate limiting** (SlowAPI + Redis on all critical endpoints)
- **Email service** (OAuth2 Gmail + SMTP fallback)
- **Loguru structured logging** (JSON logs, request tracking, rotation)
- Chart creation with geocoding (OpenCage API)
- Astronomical calculations (planets, houses, aspects)
- Chart visualization (SVG wheel with planets and aspects)
- Chart CRUD operations
- Dashboard and chart list
- PostgreSQL persistence with soft deletes
- Docker development environment
- Privacy tasks (hard delete after 30 days via Celery)
- AI interpretations (OpenAI GPT-4o-mini) - optional
- **Testing infrastructure** (~30% backend coverage, 24 auth tests)

**❌ NOT IMPLEMENTED YET:**
- Essential dignities calculation
- Sect determination (day/night)
- Lot of Fortune
- PDF generation (LaTeX infrastructure exists but no tasks)
- Higher test coverage (target: 70% backend, 60% frontend)
- Dark mode (see issue #35)
- User privacy endpoints (access, export, rectification, deletion - see issues #36-39)
- User profile management (edit name, timezone, avatar)
- Solar phase calculation (see issue #34)
- Logo integration (see issue #41)
- Internationalization
- Shared packages (`packages/shared-types/`, `packages/ui-components/`)
- Public famous charts gallery (see issue #86)

## Documentation References

- **Technical Specification:** `PROJECT_SPEC.md` (50+ pages, comprehensive requirements)
- **API Docs:** http://localhost:8000/docs (Swagger, auto-generated)
- **Getting Started:** `README.md` (setup guide)
- **OAuth Setup:** `docs/OAUTH_SETUP.md` (Google/GitHub/Facebook configuration)

## CI/CD Pipeline

**GitHub Actions:** `.github/workflows/ci.yml`

**Runs on:** Push to main/develop, Pull Requests

**Jobs:**
1. **Backend Tests** (ubuntu-latest):
   - PostgreSQL 16 + Redis 7 services
   - UV package manager for dependencies
   - Ruff linting
   - Mypy type checking (must pass with 0 errors)
   - Pytest with coverage
   - Coverage uploaded to Codecov

2. **Frontend Tests** (ubuntu-latest):
   - Node.js 20
   - ESLint linting
   - TypeScript type checking
   - Vitest with coverage
   - Build verification
   - Coverage uploaded to Codecov

3. **Monorepo Checks**:
   - Turborepo build (all apps)
   - Turborepo lint (all apps)

**Critical:** All checks must pass before merging. Mypy and Ruff have zero tolerance for errors.

## Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with hot-reload active (both frontend and backend)
3. Run tests locally: `make test`
4. **BEFORE COMMITTING: Verify CI checks pass locally**
   ```bash
   # Backend linting and type checking
   cd apps/api && uv run ruff check .
   cd apps/api && uv run mypy app/

   # Frontend linting and type checking
   cd apps/web && npm run lint
   cd apps/web && npm run type-check

   # Build verification
   cd apps/web && npm run build

   # Or run all at once
   make lint
   ```
   **CRITICAL**: All these checks MUST pass before committing. The CI pipeline runs the same checks and will fail if any errors exist.
5. Commit with Conventional Commits: `git commit -m "feat: add aspect calculation"`
6. Push and create PR (CI will run automatically)
7. Wait for CI to pass (all 3 jobs must be green: backend, frontend, build)

## Key Dependencies to Know

- **FastAPI:** Web framework (async, OpenAPI auto-generation)
- **SQLAlchemy 2.0:** ORM with async support
- **Pydantic:** Data validation and settings management
- **PySwisseph:** Astronomical calculations (Python bindings to Swiss Ephemeris)
- **React 18:** UI library
- **TypeScript 5:** Type safety
- **Vite 5:** Build tool (fast HMR)
- **TailwindCSS 3:** Utility-first CSS
- **Turborepo:** Monorepo build orchestration
