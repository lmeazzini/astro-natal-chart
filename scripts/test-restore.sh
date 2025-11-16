#!/bin/bash
# Database Restore Test Script for Astro Application
# Tests backup restoration in a temporary database
# Author: Astro DevOps Team
# Version: 1.0.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Database configuration (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-astro_user}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Test database name (will be created and destroyed)
TEST_DB="astro_restore_test_$(date +%s)"

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# Log file
LOG_FILE="${RESTORE_TEST_LOG_FILE:-/var/log/astro-restore-test.log}"

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

cleanup() {
    log "Cleaning up test database..."

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Drop test database (ignore errors)
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $TEST_DB;" 2>&1 | tee -a "$LOG_FILE" || true

    unset PGPASSWORD

    log "Cleanup completed"
}

# Trap to ensure cleanup on exit
trap cleanup EXIT INT TERM

find_latest_backup() {
    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi

    local latest=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f | sort -r | head -1)

    if [ -z "$latest" ]; then
        error "No backups found in $BACKUP_DIR"
        exit 1
    fi

    echo "$latest"
}

test_restore() {
    local backup_file="$1"

    log "Testing restore from: $(basename "$backup_file")"

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Create test database
    log "Creating test database: $TEST_DB"
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "CREATE DATABASE $TEST_DB;" 2>&1 | tee -a "$LOG_FILE"; then
        error "Failed to create test database"
        exit 1
    fi

    # Restore backup to test database
    log "Restoring backup to test database..."
    if pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$TEST_DB" \
        --verbose \
        --no-owner \
        --no-acl \
        "$backup_file" 2>&1 | tee -a "$LOG_FILE"; then
        log "Restore completed successfully ✓"
    else
        error "Restore failed"
        return 1
    fi

    unset PGPASSWORD
    return 0
}

verify_restored_data() {
    log "Verifying restored data..."

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    local exit_code=0

    # Check tables
    local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
        -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")

    log "Tables found: $table_count"

    if [ "$table_count" -eq 0 ]; then
        error "No tables found in restored database"
        exit_code=1
    fi

    # Check critical tables exist
    local required_tables=("users" "birth_charts" "oauth_accounts" "alembic_version")

    for table in "${required_tables[@]}"; do
        local exists=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
            -tAc "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table');" 2>/dev/null || echo "f")

        if [ "$exists" = "t" ]; then
            log "✓ Table exists: $table"
        else
            error "✗ Table missing: $table"
            exit_code=1
        fi
    done

    # Check record counts
    local user_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
        -tAc "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")

    local chart_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
        -tAc "SELECT COUNT(*) FROM birth_charts;" 2>/dev/null || echo "0")

    log "Users found: $user_count"
    log "Birth charts found: $chart_count"

    # Check Alembic version
    local alembic_version=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
        -tAc "SELECT version_num FROM alembic_version LIMIT 1;" 2>/dev/null || echo "")

    if [ -n "$alembic_version" ]; then
        log "Alembic version: $alembic_version ✓"
    else
        error "Alembic version not found"
        exit_code=1
    fi

    # Check database size
    local db_size=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB" \
        -tAc "SELECT pg_size_pretty(pg_database_size('$TEST_DB'));" 2>/dev/null || echo "unknown")

    log "Database size: $db_size"

    unset PGPASSWORD

    return $exit_code
}

# ============================================================================
# Main
# ============================================================================

main() {
    local backup_file="${1:-}"

    log "=========================================="
    log "Starting restore test"
    log "=========================================="

    # Find backup file
    if [ -z "$backup_file" ]; then
        log "No backup file specified, using latest backup..."
        backup_file=$(find_latest_backup)
    fi

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi

    log "Backup file: $backup_file"
    log "Test database: $TEST_DB"

    # Check prerequisites
    if ! command -v pg_restore >/dev/null 2>&1; then
        error "pg_restore not found. Please install PostgreSQL client tools."
        exit 1
    fi

    # Verify backup file
    log "Verifying backup file integrity..."
    if ! pg_restore --list "$backup_file" >/dev/null 2>&1; then
        error "Backup file appears to be corrupted"
        exit 1
    fi
    log "Backup file verified ✓"

    # Test restore
    if ! test_restore "$backup_file"; then
        error "Restore test FAILED ✗"
        exit 1
    fi

    # Verify data
    if ! verify_restored_data; then
        error "Data verification FAILED ✗"
        exit 1
    fi

    # Summary
    log "=========================================="
    log "Restore test PASSED ✓"
    log "=========================================="
    log "Backup file: $(basename "$backup_file")"
    log "All checks passed successfully"

    exit 0
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"

exit 0
