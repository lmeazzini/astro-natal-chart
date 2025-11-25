# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Upgraded Python from 3.11 to 3.13 ([#78](https://github.com/lmeazzini/astro-natal-chart/issues/78))
  - Updated all configuration files (pyproject.toml, Dockerfile, CI/CD)
  - Migrated deprecated `datetime.utcnow()` to `datetime.now(UTC)` (17 occurrences across 8 files)
  - Upgraded critical dependencies:
    - FastAPI: `0.108.0` → `>=0.115.0`
    - Pydantic: `2.5.3` → `>=2.10.0` (CRITICAL for Python 3.13 support)
    - SQLAlchemy: `2.0.25` → `>=2.0.36`
    - uvicorn: `0.25.0` → `>=0.32.0`
    - psycopg: `3.1.16` → `>=3.2.0`
    - asyncpg: `0.29.0` → `>=0.30.0` (Python 3.13 compatible)
  - Added pre-commit hook to prevent `datetime.utcnow()` reintroduction
  - Updated all documentation references to Python 3.13+

### Fixed
- Fixed SQLAlchemy model defaults to use lambda wrapper for `datetime.now(UTC)`
- Resolved Python 3.13 compatibility issues in core security, privacy, and authentication modules

---

## [Previous Releases]

For changes prior to Python 3.13 upgrade, see git history and closed PRs.
