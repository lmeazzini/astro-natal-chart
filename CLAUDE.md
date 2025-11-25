# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **natal chart (birth chart) generation system** using traditional astrology. The application provides astronomical calculations (Swiss Ephemeris), professional chart visualization, and basic astrological interpretations. The project is LGPD/GDPR compliant and handles sensitive personal data (birth date/time/location).

**Current Status**: MVP in progress (~88% complete). Core functionality is working: authentication, chart creation, calculations, and visualization. Email verification, password reset, rate limiting, LGPD/GDPR compliance (with legal documents), profile management, and backup automation all implemented.

**Tech Stack:**
- **Monorepo**: Turborepo (npm workspaces)
- **Backend**: Python 3.13+ with FastAPI (async), PostgreSQL 16 (JSONB), Redis
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

**Main calculation logic:** `apps/api/app/services/astro_service.py` (~780 lines)

**Traditional astrology modules:** `apps/api/app/astro/`
- `dignities.py` - Essential dignities (rulership, exaltation, triplicity, term, face)
- `lunar_phase.py` - Lunar phase calculations
- `solar_phase.py` - Solar phase calculations
- `temperament.py` - Traditional temperament analysis
- `lord_of_nativity_interpretations.py` - Lord of nativity interpretations
- `interpretation_prompts.yaml` - AI interpretation prompts

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
- ✅ **Sect determination** (day/night chart) - `calculate_sect()`, `calculate_sect_analysis()`
- ✅ **Arabic Parts** (Lot of Fortune, Spirit, etc.) - `calculate_arabic_parts()`
- ✅ **Essential dignities** - rulership, exaltation, triplicity, term, face (`dignities.py`)
- ✅ **Lunar phase** calculations (`lunar_phase.py`)
- ✅ **Solar phase** calculations (`solar_phase.py`)
- ✅ **Temperament** analysis (`temperament.py`)

**NOT Implemented Yet:**
- ❌ Chiron and asteroids (Ceres, Pallas, Juno, Vesta)
- ❌ Fixed stars conjunctions
- ❌ High-precision JPL DE431 ephemeris (currently using lower-precision Moshier)
- ❌ Profections, Firdaria, Solar Returns (see issues #126-128)

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

### AWS S3 Integration (PDF Storage)

**Location:** `apps/api/app/services/s3_service.py`

**Purpose:** Persistent, scalable storage for generated PDF birth chart reports.

**Key Features:**
- ✅ Upload PDFs to AWS S3 with organized folder structure
- ✅ Generate presigned URLs for secure, temporary downloads (1 hour expiration)
- ✅ Delete PDFs from S3
- ✅ List all PDFs for a chart
- ✅ Check if PDF exists in S3
- ✅ **Dev mode**: Simulates S3 operations without AWS credentials (returns local paths)
- ✅ Automatic fallback to local storage if S3 upload fails

**S3 Key Structure:**
```
s3://{bucket}/{prefix}/{user_id}/{chart_id}/{filename}
Example: s3://genesis-dev-559050210551/birth-charts/123e4567-e89b/456f-789a/full-report-20250120-153045.pdf
```

**Configuration (apps/api/.env):**
```bash
# AWS S3 - PDF Storage
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
S3_BUCKET_NAME=genesis-dev-559050210551
S3_PREFIX=birth-charts
S3_PRESIGNED_URL_EXPIRATION=3600  # 1 hour
```

**Dev Mode:** Leave `AWS_ACCESS_KEY_ID` empty to disable S3 and use local file storage.

**Usage Examples:**

```python
from app.services.s3_service import s3_service

# 1. Upload PDF from local file
s3_url = s3_service.upload_pdf(
    file_path="/tmp/chart.pdf",
    user_id="123e4567-e89b-12d3-a456-426614174000",
    chart_id="456f7890-e89b-12d3-a456-426614174001",
    filename="full-report.pdf",  # Optional, auto-generated if not provided
)
# Returns: "s3://genesis-dev-559050210551/birth-charts/123e4567.../456f7890.../full-report.pdf"
# or "file:///tmp/chart.pdf" in dev mode

# 2. Upload PDF from bytes (in-memory)
pdf_bytes = b"%PDF-1.4\n..."
s3_url = s3_service.upload_pdf_from_bytes(
    pdf_bytes=pdf_bytes,
    user_id="123e4567-e89b-12d3-a456-426614174000",
    chart_id="456f7890-e89b-12d3-a456-426614174001",
    filename="full-report.pdf",
)
# Returns: "s3://..." or "memory://..." in dev mode

# 3. Generate presigned URL for download (expires in 1 hour)
download_url = s3_service.generate_presigned_url(
    s3_url="s3://genesis-dev-559050210551/birth-charts/.../full-report.pdf",
    expires_in=3600,  # Optional, defaults to S3_PRESIGNED_URL_EXPIRATION
)
# Returns: "https://genesis-dev-559050210551.s3.amazonaws.com/...?AWSAccessKeyId=...&Signature=..."
# or None if S3 disabled or error occurred

# 4. Delete PDF from S3
success = s3_service.delete_pdf(
    s3_url="s3://genesis-dev-559050210551/birth-charts/.../full-report.pdf"
)
# Returns: True if deleted, False if error

# 5. List all PDFs for a chart
pdf_urls = s3_service.list_pdfs_for_chart(
    user_id="123e4567-e89b-12d3-a456-426614174000",
    chart_id="456f7890-e89b-12d3-a456-426614174001",
)
# Returns: ["s3://...report1.pdf", "s3://...report2.pdf"]

# 6. Check if PDF exists
exists = s3_service.pdf_exists(
    s3_url="s3://genesis-dev-559050210551/birth-charts/.../full-report.pdf"
)
# Returns: True if exists, False otherwise
```

**Integration with PDF Generation (Celery Task):**

The S3Service is integrated into the PDF generation workflow in `app/tasks/pdf_tasks.py`:

```python
# In generate_chart_pdf_task():
# 1. Generate PDF locally with LaTeX
pdf_path = pdf_service.generate_pdf_path(chart_id)

# 2. Compile PDF with pdflatex
# ... (LaTeX compilation) ...

# 3. Upload to S3 (if enabled)
s3_url = None
if s3_service.enabled:
    filename = f"full-report-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.pdf"
    s3_url = s3_service.upload_pdf(
        file_path=pdf_path,
        user_id=str(chart.user_id),
        chart_id=str(chart_id),
        filename=filename,
    )

    if s3_url:
        logger.info(f"PDF uploaded to S3: {s3_url}")
        # Clean up local file after successful upload
        pdf_path.unlink()
    else:
        logger.warning("S3 upload failed, falling back to local storage")

# 4. Save URL to database (S3 or local)
pdf_url = s3_url or f"/media/pdfs/{pdf_path.name}"
chart.pdf_url = pdf_url
chart.pdf_generated_at = datetime.now(UTC)
await db.commit()
```

**API Endpoint Integration:**

The `GET /api/v1/charts/{chart_id}/pdf-status` endpoint generates presigned URLs for S3 PDFs:

```python
from app.services.s3_service import s3_service
from app.schemas.chart import PDFDownloadResponse

@router.get("/{chart_id}/pdf-status", response_model=PDFDownloadResponse)
async def get_pdf_status(
    chart_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PDFDownloadResponse:
    # ... (fetch chart from database) ...

    if chart.pdf_url.startswith("s3://"):
        # Generate presigned URL for S3
        download_url = s3_service.generate_presigned_url(
            s3_url=chart.pdf_url,
            expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
        )
        expires_in = settings.S3_PRESIGNED_URL_EXPIRATION
    else:
        # Local file path (dev mode)
        download_url = chart.pdf_url
        expires_in = None

    return PDFDownloadResponse(
        status="ready",
        download_url=download_url,
        expires_in=expires_in,
        generated_at=chart.pdf_generated_at,
        message="PDF is ready for download.",
    )
```

**Security Considerations:**
- **Private bucket**: S3 bucket is private, no public access
- **Presigned URLs**: Temporary URLs with 1-hour expiration
- **IAM policies**: Least-privilege access (PutObject, GetObject, DeleteObject only)
- **Path traversal protection**: Filenames sanitized to prevent `../../` attacks
- **User isolation**: PDFs organized by user_id to prevent cross-user access

**Testing:**

Comprehensive tests in `apps/api/tests/test_services/test_s3_service.py`:
- ✅ Initialization with/without credentials
- ✅ S3 key building and path traversal protection
- ✅ Upload from file (success, file not found, client errors)
- ✅ Upload from bytes (success, dev mode)
- ✅ Presigned URL generation (success, invalid URLs, disabled mode)
- ✅ Delete PDF (success, invalid URLs, dev mode)
- ✅ List PDFs (success, empty results, disabled mode)
- ✅ PDF existence checks (exists, not found, invalid URLs)

**Cost Estimation:**
- Storage: $0.023/GB/month (S3 Standard)
- Requests: $0.005 per 1,000 PUT requests, $0.0004 per 1,000 GET requests
- Data transfer: First 100GB/month free, then $0.09/GB
- **Example**: 1,000 PDFs (2MB each, 2GB total) = ~$0.05/month storage + ~$0.01/month requests = **< $1/month**

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

**CURRENT STATUS**: **439 tests** collected, backend coverage improving

**Backend testing (pytest):**
- `apps/api/tests/test_api/` - API endpoint tests (auth, charts, users, etc.)
- `apps/api/tests/test_astro/` - Astrological calculation tests
  - `test_dignities.py` - Essential dignities tests
- `apps/api/tests/test_services/` - Service layer tests
  - `test_astro_service.py` - Astro calculations (sect, aspects, etc.)
  - `test_chart_service.py` - Chart CRUD operations
  - `test_geocoding_service.py` - Location lookup
  - `test_interpretation_service.py` - AI interpretations
  - `test_interpretation_cache_service.py` - Cache logic
  - `test_pdf_service.py` - PDF generation
  - `test_s3_service.py` - S3 storage
  - `test_rag_services.py` - RAG/Qdrant integration
  - `test_backup_s3_service.py` - Backup service

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
6. **Empty directories:** `packages/` exists but is empty/unused
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
- **LGPD/GDPR compliance** (Issue #6)
  - Privacy endpoints (export data, delete account, cancel deletion)
  - User consent tracking (UserConsent model)
  - Audit logs (5 year retention)
  - Privacy tasks via Celery (auto cleanup after 30 days)
- **Profile management** (Issue #12)
  - View/edit profile (name, timezone, locale)
  - Change password
  - User statistics and activity log
  - OAuth connections management
  - Account deletion (soft + hard delete)
- **Backup automation** (Issue #7)
  - Professional backup script (PostgreSQL)
  - 30-day retention, compression, S3 upload
  - Integrity verification, healthcheck integration
- **Legal documents** (LGPD/GDPR compliant)
  - Terms of Service (`docs/TERMS_OF_SERVICE.md`)
  - Privacy Policy (`docs/PRIVACY_POLICY.md`)
  - Cookie Policy (`docs/COOKIE_POLICY.md`)
  - DPO contact, data retention policies
- Chart creation with geocoding (OpenCage API)
- Astronomical calculations (planets, houses, aspects)
- Chart visualization (SVG wheel with planets and aspects)
- Chart CRUD operations
- Dashboard and chart list
- PostgreSQL persistence with soft deletes
- Docker development environment
- Redis for caching and rate limiting
- AI interpretations (OpenAI GPT-4o-mini) - optional
- **Testing infrastructure** (439 tests, backend coverage improving)
- **Traditional Astrology Calculations:**
  - ✅ Sect determination (day/night chart)
  - ✅ Arabic Parts (Lot of Fortune, Spirit, etc.)
  - ✅ Essential dignities (rulership, exaltation, triplicity, term, face)
  - ✅ Lunar phase calculations
  - ✅ Solar phase calculations
  - ✅ Temperament analysis
  - ✅ RAG system with Qdrant for AI interpretations

**❌ NOT IMPLEMENTED YET:**
- Disaster recovery tests and restore procedures (see issue #87)
- Chiron and asteroids
- Fixed stars conjunctions
- PDF generation (LaTeX infrastructure exists but no tasks)
- Higher test coverage (target: 70% backend, 60% frontend)
- Dark mode (see issue #35)
- Avatar upload (profile management endpoints exist)
- Logo integration (see issue #41)
- Internationalization (i18n)
- Cache logic for astro calculations (Redis configured but not used for caching yet)
- Shared packages (`packages/shared-types/`, `packages/ui-components/`)
- Public famous charts gallery (see issue #86)
- Blog with SEO optimization (planned)
- Profections, Firdaria, Solar Returns (see issues #126-128)

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

### GitFlow Strategy

We use a simplified GitFlow with two main branches:

- **`main`** (🔴 Production): Stable code only, protected, auto-deploy to production
- **`dev`** (🟡 Development): Default branch, active development, auto-deploy to staging

**Branch types:**
- `feature/*` - New functionality
- `fix/*` - Bug corrections
- `chore/*` - Maintenance tasks
- `docs/*` - Documentation
- `refactor/*` - Code improvements
- `test/*` - Test additions
- `hotfix/*` - Critical production fixes (from `main`)

### ⚠️ COMMIT RULES (CRITICAL)

| Branch | Direct Commit Allowed? | When? |
|--------|------------------------|-------|
| `main` | 🚫 **NEVER** | Only via PR from `dev` (releases) or `hotfix/*` |
| `dev` | 🚫 **NO** | Only if **explicitly requested** by user |
| `feature/*` | ✅ Yes | Normal development |

**Golden Rules:**
1. **New feature?** → Create `feature/xxx` branch → PR to `dev`
2. **Bug fix?** → Create `fix/xxx` branch → PR to `dev`
3. **Hotfix in production?** → Create `hotfix/xxx` from `main` → PR to `main` AND `dev`
4. **Release?** → PR from `dev` to `main` → Create tag and GitHub release

### Workflow Steps

1. **Create feature branch from `dev`:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/my-feature
   ```

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

6. Push and create PR **to `dev`** (CI will run automatically):
   ```bash
   git push origin feature/my-feature
   gh pr create --base dev --title "feat: add aspect calculation"
   ```

7. Wait for CI to pass (all 3 jobs must be green: backend, frontend, build)

8. After approval, merge to `dev`

### Release Process (dev → main)

When ready to release:

```bash
# 1. Create PR from dev to main
gh pr create --base main --head dev --title "Release vX.Y.Z"

# 2. After PR is merged, create tag and release
git checkout main
git pull origin main
git tag -a vX.Y.Z -m "Release vX.Y.Z: brief description"
git push origin vX.Y.Z

# 3. Create GitHub release
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Release notes here"
```

**Versioning (SemVer):**
- `vX.0.0` - Major: Breaking changes
- `vX.Y.0` - Minor: New features (backward compatible)
- `vX.Y.Z` - Patch: Bug fixes

### Hotfix Process

For critical production bugs:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug, commit, push

# 3. Create PR to main
gh pr create --base main --title "hotfix: fix critical bug"

# 4. After merge, also merge to dev
git checkout dev
git merge main
git push origin dev
```

**IMPORTANT:**
- **NEVER** commit directly to `main` or `dev` (unless explicitly requested for `dev`)
- **ALWAYS** create PRs to `dev` for features/fixes
- **ALWAYS** create tag + release when merging `dev` → `main`
- See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for full guidelines

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
