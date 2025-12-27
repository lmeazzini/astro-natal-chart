# Database Migrations Guide

This document provides comprehensive guidance for managing Alembic database migrations in the Real Astrology project.

## Quick Reference

| Command | Description |
|---------|-------------|
| `make migrate` | Apply all pending migrations |
| `make migrate-create` | Create a new migration (autogenerate) |
| `make migrate-down` | Rollback one migration |
| `make migrate-status` | Show current migration state |
| `make migrate-check` | Verify migration integrity |
| `make db-reset` | Reset database (DESTRUCTIVE) |

## Current State

- **Total Migrations**: 30
- **Database**: PostgreSQL 16 (async with JSONB support)
- **Framework**: Alembic with SQLAlchemy 2.0 async
- **All migrations have `downgrade()` implemented** ✅

---

## Creating New Migrations

### Step 1: Modify Your Models

Edit the SQLAlchemy models in `apps/api/app/models/`:

```python
# apps/api/app/models/my_model.py
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### Step 2: Ensure Model is Imported

Add your model import to `apps/api/alembic/env.py`:

```python
# Import all models for Alembic autogenerate to detect them
from app.models.my_model import MyModel  # Add this line
```

### Step 3: Generate Migration

```bash
make migrate-create
# Or manually:
cd apps/api && alembic revision --autogenerate -m "add_my_models_table"
```

### Step 4: Review Generated Migration

**ALWAYS review the generated migration file** in `apps/api/alembic/versions/`:

```python
def upgrade() -> None:
    op.create_table(
        "my_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_my_models_id"), "my_models", ["id"], unique=False)

def downgrade() -> None:
    op.drop_index(op.f("ix_my_models_id"), table_name="my_models")
    op.drop_table("my_models")
```

### Step 5: Apply Migration

```bash
make migrate
```

---

## Pre-Deployment Checklist

Before deploying migrations to production:

- [ ] **Backup production database**
  ```bash
  ./scripts/backup-db.sh
  ```

- [ ] **Test migration in staging/development**
  ```bash
  make migrate
  ```

- [ ] **Verify downgrade works**
  ```bash
  make migrate-down
  make migrate  # Re-apply
  ```

- [ ] **Check for data-destructive operations**
  - `DROP TABLE` / `DROP COLUMN` - Will lose data!
  - `ALTER COLUMN` type changes - May fail with existing data
  - Review migration SQL:
    ```bash
    cd apps/api && alembic upgrade head --sql
    ```

- [ ] **Check migration chain integrity**
  ```bash
  make migrate-check
  ```

- [ ] **Verify no multiple heads**
  ```bash
  cd apps/api && alembic heads
  # Should show only ONE head
  ```

---

## Production Deployment Procedure

### Standard Deployment

1. **Create backup** (automated in CI/CD, but verify):
   ```bash
   ./scripts/backup-db.sh
   ```

2. **Check current state**:
   ```bash
   make migrate-status
   ```

3. **Apply migrations**:
   ```bash
   make migrate
   ```

4. **Verify success**:
   ```bash
   make migrate-status
   ```

### Zero-Downtime Migrations

For migrations that require no downtime:

1. **Additive changes only** (safe):
   - `ADD COLUMN` with `NULL` or `DEFAULT`
   - `CREATE TABLE`
   - `CREATE INDEX CONCURRENTLY`

2. **Two-phase deployment** (for breaking changes):
   - Phase 1: Add new column (nullable)
   - Deploy code that writes to both old and new
   - Phase 2: Migrate data, make column required
   - Phase 3: Remove old column

---

## Rollback Procedures

### Rollback One Migration

```bash
make migrate-down
# Or:
cd apps/api && alembic downgrade -1
```

### Rollback to Specific Revision

```bash
cd apps/api && alembic downgrade <revision_id>
# Example:
cd apps/api && alembic downgrade 14f966eaec6d
```

### Rollback All Migrations

```bash
cd apps/api && alembic downgrade base
```

### Emergency Rollback with Database Restore

If migration corrupted data:

```bash
# 1. Stop application
docker compose down

# 2. Restore from backup
./scripts/restore-db.sh backups/astro_backup_YYYYMMDD_HHMMSS.sql.gz

# 3. Sync Alembic to match restored state
cd apps/api && alembic stamp <last_known_good_revision>

# 4. Restart application
docker compose up -d
```

---

## Troubleshooting

### Table Already Exists

**Error**: `sqlalchemy.exc.ProgrammingError: relation "table_name" already exists`

**Cause**: Migration was partially applied or table was created manually.

**Solution**:
```bash
# Option 1: Mark migration as applied (if table is correct)
cd apps/api && alembic stamp head

# Option 2: Drop the table and re-run migration
# (Only if data loss is acceptable)
psql -U astro -d astro_dev -c "DROP TABLE table_name CASCADE;"
make migrate
```

### Multiple Heads Detected

**Error**: `alembic.util.exc.CommandError: Multiple heads are present`

**Cause**: Parallel development created branching migrations.

**Solution**:
```bash
# 1. List the heads
cd apps/api && alembic heads

# 2. Create merge migration
cd apps/api && alembic merge heads -m "merge_multiple_heads"

# 3. Apply
make migrate
```

### Migration State Out of Sync

**Cause**: Database was modified outside of Alembic.

**Solution**:
```bash
# 1. Check current state
cd apps/api && alembic current

# 2. If database is ahead of Alembic, stamp to current state
cd apps/api && alembic stamp <actual_revision>

# 3. If database is behind, apply missing migrations
make migrate
```

### Foreign Key Constraint Errors

**Error**: `cannot drop table because other objects depend on it`

**Solution**:
1. Check migration order - parent tables must be created before children
2. Use `CASCADE` in downgrade:
   ```python
   def downgrade():
       op.drop_table("child_table")  # Drop children first
       op.drop_table("parent_table")
   ```

---

## Best Practices

### Naming Conventions

- Migrations use format: `YYYY_MM_DD_HHMM-{revision}_{slug}.py`
- Use descriptive slugs: `add_users_table`, `add_email_index`, `rename_status_column`

### Index Naming

Use `op.f()` for consistent, auto-generated index names:
```python
op.create_index(op.f("ix_users_email"), "users", ["email"])
```

### Column Defaults

Always specify `server_default` for new columns on existing tables:
```python
sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"))
```

### JSONB Columns

Use PostgreSQL JSONB for flexible data:
```python
from sqlalchemy.dialects import postgresql
sa.Column("metadata", postgresql.JSONB, nullable=True)
```

### UUID Primary Keys

Always use UUID for primary keys:
```python
from sqlalchemy.dialects.postgresql import UUID
sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
```

### Soft Deletes

Use `deleted_at` timestamp instead of hard deletes:
```python
sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
```

### Always Implement Downgrade

Every `upgrade()` must have a corresponding `downgrade()`:
```python
def upgrade():
    op.add_column("users", sa.Column("phone", sa.String(20)))

def downgrade():
    op.drop_column("users", "phone")
```

---

## Migration History

To view migration history:

```bash
# Full history
cd apps/api && alembic history

# Verbose with dates
cd apps/api && alembic history -v

# Last 10 migrations
cd apps/api && alembic history -v | head -30
```

---

## Related Documentation

- [Alembic Official Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy Migration Best Practices](https://docs.sqlalchemy.org/en/20/core/metadata.html#altering-database-objects-through-migrations)
- Issue #7: Backup automation
- Issue #87: Disaster recovery tests

---

## Appendix: Current Migrations (30 total)

| Date | Revision | Description |
|------|----------|-------------|
| 2025-11-14 | 14f966eaec6d | Initial migration |
| 2025-11-15 | 22f518a0295f | Add chart_interpretations table |
| 2025-11-15 | 2d5eb21ce250 | Add password_reset_tokens table |
| 2025-11-15 | 26cd00243413 | Add user_consents table |
| 2025-11-16 | 7b0e1bdd69f5 | Add deleted_at to users table |
| 2025-11-16 | 5d7ee6340019 | Add user profile fields |
| 2025-11-17 | b47c6865ccaf | Add async processing fields |
| 2025-11-20 | b6028633621c | Add PDF fields to birth_charts |
| 2025-11-20 | b0ef95f73d85 | Add password_changed_at field |
| 2025-11-20 | ccc076a63ea8 | Add updated_at triggers |
| 2025-11-20 | 17d797292022 | Add pdf_generating and pdf_task_id |
| 2025-11-22 | 44bae117595b | Add interpretation_cache table |
| 2025-11-22 | 99dbbd3990dd | Add role to users table |
| 2025-11-22 | 2f5d48c07f14 | Add user profile expansion fields |
| 2025-11-22 | 93b7ace49920 | Merge multiple heads |
| 2025-11-22 | (vector) | Add RAG vector documents |
| 2025-11-22 | (time) | Add time_format to users |
| 2025-11-23 | 303700b12232 | Merge RAG and other heads |
| 2025-11-23 | a353cbccb342 | Add public_charts table |
| 2025-11-23 | 61837bbf83a1 | Add rag_sources to interpretations |
| 2025-11-23 | 782ba409672f | Add public_chart_interpretations |
| 2025-11-24 | 568668ec858b | Add language to interpretations |
| 2025-11-24 | 9b5e1a052466 | Add language to public_chart |
| 2025-11-24 | 13342d0a1b93 | Rename geral to free, add premium role |
| 2025-11-25 | 7a6c838f8b19 | Add blog_posts table |
| 2025-11-25 | 55361a122379 | Add is_featured to blog_posts |
| 2025-11-25 | 6965ccdd2487 | Add subscriptions table |
| 2025-11-29 | 328917e74f78 | Add unique constraint to chart |
| 2025-11-30 | cec026704f64 | Add i18n columns to public_charts |
| 2025-12-23 | a1b2c3d4e5f6 | Add subscription_history table |
