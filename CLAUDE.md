# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Natal chart (birth chart) generation system** using traditional astrology. Provides astronomical calculations (Swiss Ephemeris), professional chart visualization, and astrological interpretations. LGPD/GDPR compliant.

**Tech Stack:**
- **Monorepo**: Turborepo (npm workspaces)
- **Backend**: Python 3.13+ with FastAPI (async), PostgreSQL 16 (JSONB), Redis
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Astrology Engine**: PySwisseph (Moshier ephemeris - built-in)
- **Infrastructure**: Docker Compose for development

## Essential Commands

### Quick Start
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
make docker-up && make migrate
```

### Development
```bash
make dev              # Start all services (Turborepo)
make test             # Run all tests
make lint             # Lint all code
make format           # Format all code
```

### Backend (UV Package Manager)
```bash
cd apps/api
uv sync               # Install dependencies
uv add package-name   # Add dependency
uv run pytest         # Run tests
uv run ty check app/  # Type checking
uv run ruff check .   # Linting
```

### Database (Alembic)
```bash
make migrate          # Run migrations
make migrate-create   # Create new migration (autogenerate)
make migrate-down     # Rollback last migration
```

### Docker
```bash
make docker-up        # Start services
make docker-down      # Stop services
make docker-logs      # View logs
make docker-rebuild   # Rebuild and restart
```

### CI Verification (MANDATORY Before Commit)
```bash
cd apps/api && uv run ruff check . && uv run ty check app/
cd apps/web && npm run lint && npm run type-check && npm run build
```
All checks must pass - ty and Ruff have **zero tolerance** for errors.

## Architecture

### Monorepo Structure
```
apps/
  api/           # Python FastAPI backend
  web/           # React TypeScript frontend
packages/        # (empty - planned for future)
```

### Backend Layers
1. **API** (`app/api/v1/endpoints/`): Routes, request/response
2. **Service** (`app/services/`): Business logic
3. **Repository** (`app/repositories/`): Data access (BaseRepository pattern)
4. **Models** (`app/models/`): SQLAlchemy models

**Key patterns:** Async everywhere, Dependency Injection (`Depends()`), Repository pattern

**Critical models:**
- `User`: email, password_hash, OAuth relationships
- `BirthChart`: person_name, birth_datetime (TZ-aware), lat/lon, `chart_data` (JSONB)
- `AuditLog`: LGPD/GDPR compliance tracking

**Authentication:** JWT (access: 15 min, refresh: 30 days), OAuth2 (Google, GitHub, Facebook)

### Frontend Structure
- `src/pages/`: Route components
- `src/components/`: Reusable UI (ChartWheel, PlanetList, AspectGrid)
- `src/services/`: API client (fetch-based)
- `src/contexts/`: AuthContext

**State:** React Context + useState (React Query/Zustand installed but unused)

### Chart Data Structure (JSONB)
```json
{
  "planets": [{"name": "Sun", "longitude": 45.123, "sign": "Taurus", "house": 10, "retrograde": false}],
  "houses": [{"number": 1, "cusp": 123.456, "sign": "Leo"}],
  "aspects": [{"planet1": "Sun", "planet2": "Moon", "aspect": "trine", "orb": 2.3, "applying": true}],
  "chart_info": {"ascendant": 123.456, "mc": 234.567}
}
```

## Astrological Calculations

**Main logic:** `apps/api/app/services/astro_service.py`
**Traditional modules:** `apps/api/app/astro/` (dignities, lunar_phase, solar_phase, temperament)

**Implemented:**
- ✅ Planet positions (Sun through Pluto + North Node)
- ✅ House systems (Placidus, Koch, Equal, Whole Sign, Campanus, Regiomontanus)
- ✅ Aspects with orbs, applying/separating detection
- ✅ Sect (day/night), Arabic Parts, Essential Dignities
- ✅ Lunar/Solar phases, Temperament analysis
- ✅ Saturn Return, Solar Return calculations
- ✅ RAG system with Qdrant for AI interpretations

**Not implemented:** Chiron/asteroids, Fixed stars, High-precision JPL DE431

## Key Services

### Celery Tasks (`app/tasks/`)
- `cleanup_deleted_users()`: Hard delete after 30-day retention (LGPD)
- Runs via Celery Beat (Redis broker)

### S3 Service (`app/services/s3_service.py`)
PDF storage with presigned URLs. Dev mode simulates locally when `AWS_ACCESS_KEY_ID` empty.

### Amplitude Analytics
~70 events across auth, charts, profile, premium categories.
See `docs/AMPLITUDE_BEST_PRACTICES.md` for event naming and usage.

### Email Service
OAuth2 Gmail + SMTP fallback for verification and password reset.

## Design System — "Midnight & Paper"

**CRITICAL**: Follow `ux/DESIGN_REFERENCE.md` for all UI work.

- **Light**: Cream background, midnight blue text, gold accents
- **Dark**: Deep space blue background, warm cream text
- **Typography**: Playfair Display (headings), Inter (body)
- **Spacing**: 8px grid, `rounded-full` buttons, `rounded-2xl` cards

Use CSS variables (`--primary`, `--accent`, `--background`) - never hardcode colors.

### Quick Visual Check

**IMMEDIATELY** after implementing any front-end change:

1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md` and `/context/style-guide.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take full page screenshot at desktop viewport (1440px) of each changed view
7. **Check for errors** - Run `mcp__playwright__browser_console_messages`

This verification ensures changes meet design standards and user requirements.

### Comprehensive Design Review

Invoke the `@design-review-agent` subagent for thorough design validation when:

- Completing significant UI/UX features
- Before finalizing PRs with visual changes
- Needing comprehensive accessibility and responsiveness testing

## Development Patterns

### Adding API Endpoint
1. Create schemas in `app/schemas/`
2. Add business logic in `app/services/`
3. Create route in `app/api/v1/endpoints/`
4. Use `Depends(get_current_user)` for auth

### Adding Database Model
1. Create model in `app/models/`
2. Import in `alembic/env.py`
3. Run `make migrate-create` then `make migrate`

Use UUID primary keys and timezone-aware datetimes.

### Adding React Component
1. Use TypeScript with explicit prop types
2. Use Tailwind + `cn()` utility for styling
3. Follow Design Reference

## Security & Compliance

- **NEVER** commit `.env` files
- Password hashing: bcrypt (cost 12)
- Audit logging for all sensitive actions
- Soft deletes with 30-day retention
- Rate limiting: SlowAPI + Redis (`RATE_LIMIT_ENABLED=false` for tests)

## Testing

**Status:** 439+ tests, coverage improving

```bash
cd apps/api && pytest --cov=app    # Backend
cd apps/web && npm run test        # Frontend
```

**Fixtures:** `db_session`, `test_user`, `test_user_factory`, `test_chart_factory`

## Git Workflow

**Branches:** `main` (production), `dev` (development)

| Branch | Direct Commit? |
|--------|----------------|
| `main` | 🚫 NEVER |
| `dev` | 🚫 Only if explicitly requested |
| `feature/*` | ✅ Yes |

**Flow:**
1. Create branch from `dev`: `git checkout -b feature/xxx`
2. Write tests first (TDD)
3. Implement, run `make lint`
4. PR to `dev`: `gh pr create --base dev`

See `CONTRIBUTING.md` for full guidelines.

## Common Pitfalls

1. **Alembic migrations not detected:** Import model in `alembic/env.py`
2. **Async/sync mismatch:** Backend is fully async
3. **JSONB queries:** Use PostgreSQL operators (`->`, `->>`, `@>`)
4. **Timezone handling:** Always use TZ-aware datetimes
5. **Docker watchfiles crash:** Don't remove `.venv` exclusions from docker-compose.yml

## Environment Variables

**Backend** (`apps/api/.env`):
- `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`
- OAuth: `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID`, `FACEBOOK_CLIENT_ID` + secrets
- `OPENCAGE_API_KEY`, `OPENAI_API_KEY`, `AMPLITUDE_API_KEY`
- AWS: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME`

**Frontend** (`apps/web/.env`):
- `VITE_API_URL`, `VITE_GOOGLE_CLIENT_ID`, `VITE_AMPLITUDE_API_KEY`

## Documentation

- **Spec:** `PROJECT_SPEC.md`
- **Design:** `ux/DESIGN_REFERENCE.md`
- **API:** http://localhost:8000/docs
- **OAuth:** `docs/OAUTH_SETUP.md`
- **Analytics:** `docs/AMPLITUDE_BEST_PRACTICES.md`
