# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **natal chart (birth chart) generation system** using traditional astrology. The application provides high-precision astronomical calculations (Swiss Ephemeris), professional chart visualization, and detailed astrological interpretations. The project is LGPD/GDPR compliant and handles sensitive personal data (birth date/time/location).

**Tech Stack:**
- **Monorepo**: Turborepo (npm workspaces)
- **Backend**: Python 3.11+ with FastAPI (async), PostgreSQL 16 (JSONB), Celery + Redis
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Astrology Engine**: PySwisseph (Swiss Ephemeris, JPL DE431 ephemeris)
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
packages/        # Shared code (future: shared-types, ui-components)
```

All apps are orchestrated by **Turborepo** (`turbo.json`). Running `npm run dev` from root executes both frontend and backend in parallel.

### Backend Architecture (FastAPI)

**Layered architecture:**
1. **API Layer** (`app/api/v1/`): FastAPI routes, request/response handling
2. **Service Layer** (`app/services/`): Business logic orchestration
3. **Domain Layer** (`app/astro/`): Astrological calculation engine (core logic)
4. **Data Layer** (`app/models/`): SQLAlchemy models, database access

**Key patterns:**
- **Async everywhere**: SQLAlchemy async engine, FastAPI async endpoints
- **Dependency Injection**: FastAPI's `Depends()` for `get_db()` and `get_current_user()`
- **Repository pattern** (planned): Abstract database access in services

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
- `src/pages/`: Route components (HomePage, LoginPage, ChartViewPage, etc.)
- `src/components/`: Reusable UI components organized by domain (auth/, chart/, ui/, layout/)
- `src/services/`: API client (axios instance with interceptors)
- `src/hooks/`: Custom React hooks (useAuth, useCharts, etc.)
- `src/utils/`: Utility functions (cn for className merging, validators, formatters)

**State management:**
- **React Query** (@tanstack/react-query) for server state (API data caching)
- **Zustand** (lightweight) or React Context for client state (if needed)
- **React Hook Form + Zod** for form state and validation

**API communication:**
- Axios instance in `src/services/api.ts` with interceptors
- Request interceptor adds JWT from localStorage
- Response interceptor handles 401 (redirect to login)

### Astrological Calculations (Critical Domain Logic)

**Location in codebase:** `apps/api/app/astro/`

**Planned modules:**
- `calculator.py`: Main calculation orchestrator
- `planets.py`: Planetary positions using PySwisseph
- `houses.py`: House cusp calculations (Placidus, Whole Sign, Koch, etc.)
- `aspects.py`: Aspect detection with orbs
- `dignities.py`: Essential dignities (rulership, exaltation, triplicity, term, face)
- `interpretations.py`: Text generation from templates

**Critical requirements:**
- Use **Swiss Ephemeris** (PySwisseph) for all calculations
- Precision requirement: < 1 arcsecond error
- Support multiple house systems (Placidus default, but also Whole Sign, Koch, etc.)
- Calculate sect (day/night chart) based on Sun position relative to horizon
- Store ephemeris files path in `EPHEMERIS_PATH` env var (default: `/usr/share/ephe`)

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
      "house": 10,
      "dignities": {
        "ruler": false,
        "exaltation": false,
        "total_score": 4
      }
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
      "orb": 2.3,
      "applying": true
    }
  ],
  "chart_info": {
    "ascendant": 123.456,
    "mc": 234.567,
    "sect": "diurnal",
    "lot_of_fortune": 198.765
  }
}
```

### Celery Async Tasks

**Location:** `apps/api/app/tasks/`

**Use cases:**
- PDF generation (heavy LaTeX compilation)
- Bulk chart calculations
- Email sending (future)

**Setup:**
- Celery worker runs in separate Docker container
- Redis as message broker and result backend
- Task results stored in Redis with TTL

### Environment Configuration

**Backend** (`apps/api/.env`):
- `DATABASE_URL`: PostgreSQL async URL (postgresql+asyncpg://...)
- `SECRET_KEY`: For JWT signing (CRITICAL - change in production)
- OAuth2 credentials: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, etc.
- `OPENCAGE_API_KEY`: For geocoding (location search)
- `EPHEMERIS_PATH`: Path to Swiss Ephemeris data files

**Frontend** (`apps/web/.env`):
- `VITE_API_URL`: Backend API URL (http://localhost:8000 in dev)
- OAuth2 client IDs (for frontend OAuth buttons)

## Critical Development Patterns

### Adding New API Endpoint

1. Create Pydantic schemas in `app/schemas/` (request/response)
2. Add business logic in `app/services/`
3. Create route in `app/api/v1/`
4. Use `Depends(get_current_user)` for authenticated endpoints
5. Document with FastAPI docstrings (auto-generates OpenAPI)

Example:
```python
# app/api/v1/charts.py
@router.post("/", response_model=ChartRead, status_code=201)
async def create_chart(
    chart_data: ChartCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await chart_service.create_chart(db, chart_data, current_user.id)
```

### Adding Database Model

1. Create model in `app/models/` (inherit from `Base`)
2. Import model in `alembic/env.py` (for autogenerate to detect it)
3. Create migration: `make migrate-create`
4. Review generated migration in `alembic/versions/`
5. Apply: `make migrate`

**Critical:** Always use UUID primary keys (`uuid4()`) and timezone-aware datetimes.

### Adding React Component

1. Create in appropriate subdirectory (`src/components/ui/`, `src/components/chart/`, etc.)
2. Use TypeScript with explicit prop types
3. Use Tailwind for styling
4. Use `cn()` utility from `@/utils/cn` for conditional classes
5. Extract form logic to custom hooks if complex

### Form Validation Pattern

Always use Zod + React Hook Form:
```typescript
const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema),
});
```

### API Call Pattern

Use React Query for all API calls:
```typescript
const { data, isLoading, error } = useQuery({
  queryKey: ['charts'],
  queryFn: () => chartService.getCharts(),
});
```

## Security & Compliance

- **NEVER** commit `.env` files or secrets
- **Password hashing:** bcrypt with cost factor 12
- **Sensitive data:** Birth date/time/location are personal data (LGPD/GDPR)
- **Audit logging:** Log all chart creations, deletions, user logins
- **Soft deletes:** `deleted_at` timestamp, hard delete after 30 days
- **CORS:** Configured in backend (`ALLOWED_ORIGINS`)
- **Rate limiting:** TODO - implement before production

## Testing Guidelines

- **Backend:** Use pytest fixtures for DB setup (transaction rollback)
- **Astrological calculations:** Validate against known cases (compare with astro.com)
- **Frontend:** Use Testing Library, avoid implementation details
- Coverage target: 70% minimum

## Docker Services

When running `docker-compose up -d`, these services start:

1. **db** (postgres:16-alpine) - Port 5432
2. **redis** (redis:7-alpine) - Port 6379
3. **api** (FastAPI) - Port 8000, depends on db+redis
4. **celery_worker** (Celery) - No exposed port, depends on db+redis
5. **web** (React+Vite) - Port 5173, depends on api

All services are on `astro-network` bridge network with persistent volumes for postgres and redis data.

## Common Pitfalls

1. **Alembic migrations not detected:** Ensure model is imported in `alembic/env.py`
2. **Async/sync mismatch:** Backend is fully async - use `async def` and `await`
3. **JSONB queries:** Use PostgreSQL JSONB operators (`->`, `->>`, `@>`) for querying chart_data
4. **Timezone handling:** Always use timezone-aware datetimes, store birth_timezone IANA name
5. **PySwisseph path:** Ephemeris files must be downloaded separately and path configured

## Documentation References

- **Technical Specification:** `PROJECT_SPEC.md` (50+ pages, comprehensive requirements)
- **API Docs:** http://localhost:8000/docs (Swagger, auto-generated)
- **Getting Started:** `GETTING_STARTED.md` (setup guide)
- **Backend Details:** `apps/api/README.md`
- **Frontend Details:** `apps/web/README.md`

## Development Workflow

1. Create feature branch: `git checkout -b feature/name`
2. Make changes with hot-reload active (both frontend and backend)
3. Write tests: `make test`
4. Lint: `make lint`
5. Commit with Conventional Commits: `git commit -m "feat: add aspect calculation"`
6. Push and create PR

## Key Dependencies to Know

- **FastAPI:** Web framework (async, OpenAPI auto-generation)
- **SQLAlchemy 2.0:** ORM with async support
- **Pydantic:** Data validation and settings management
- **PySwisseph:** Astronomical calculations (Python bindings to Swiss Ephemeris)
- **React Query:** Server state management and caching
- **Zod:** Schema validation (TypeScript)
- **Turborepo:** Monorepo build orchestration
