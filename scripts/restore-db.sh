#!/bin/bash
# Database Restore Script for Astro Application
# Restores PostgreSQL database from backup file
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
DB_NAME="${DB_NAME:-astro}"
DB_USER="${DB_USER:-astro_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"

# Docker configuration
DOCKER_COMPOSE="${DOCKER_COMPOSE:-docker compose}"
STOP_SERVICES="${RESTORE_STOP_SERVICES:-true}"

# Log file
LOG_FILE="${RESTORE_LOG_FILE:-/var/log/astro-restore.log}"

# Default backup directory
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

usage() {
    cat <<EOF
Usage: $0 <backup_file> [options]

Restore PostgreSQL database from backup file.

Arguments:
    backup_file         Path to backup file (*.sql.gz)

Options:
    --no-stop           Don't stop application services
    --no-confirm        Skip confirmation prompt (dangerous!)
    --download-s3       Download latest backup from S3 first
    --list-backups      List available local backups
    --help              Show this help message

Environment Variables:
    DB_HOST             Database host (default: localhost)
    DB_PORT             Database port (default: 5432)
    DB_NAME             Database name (default: astro)
    DB_USER             Database user (default: astro_user)
    DB_PASSWORD         Database password
    POSTGRES_USER       PostgreSQL admin user (default: postgres)
    BACKUP_DIR          Backup directory (default: /var/backups/astro-db)

Examples:
    # Restore from local backup
    $0 /var/backups/astro-db/astro_backup_20250116_030000.sql.gz

    # Restore without confirmation (use with caution!)
    $0 backup.sql.gz --no-confirm

    # List available backups
    $0 --list-backups

    # Download and restore latest S3 backup
    $0 --download-s3

EOF
    exit 0
}

list_backups() {
    log "Available backups in $BACKUP_DIR:"
    echo ""

    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi

    # List backups with details
    local backups=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f | sort -r)

    if [ -z "$backups" ]; then
        echo "No backups found in $BACKUP_DIR"
        exit 0
    fi

    echo "Recent backups:"
    echo ""
    printf "%-40s %-12s %-20s\n" "FILENAME" "SIZE" "DATE"
    echo "--------------------------------------------------------------------------------"

    echo "$backups" | head -10 | while read -r backup; do
        local filename=$(basename "$backup")
        local size=$(ls -lh "$backup" | awk '{print $5}')
        local date=$(ls -l --time-style=long-iso "$backup" 2>/dev/null | awk '{print $6" "$7}' || stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$backup")

        printf "%-40s %-12s %-20s\n" "$filename" "$size" "$date"
    done

    echo ""
    exit 0
}

download_from_s3() {
    local s3_bucket="${BACKUP_S3_BUCKET:-}"
    local s3_prefix="${BACKUP_S3_PREFIX:-backups}"

    if [ -z "$s3_bucket" ]; then
        error "S3_BUCKET not configured"
        exit 1
    fi

    if ! command -v aws >/dev/null 2>&1; then
        error "AWS CLI not installed"
        exit 1
    fi

    log "Downloading latest backup from S3..."

    # List backups in S3
    local latest=$(aws s3 ls "s3://${s3_bucket}/${s3_prefix}/" --recursive | \
        grep "astro_backup_.*\.sql\.gz$" | \
        sort -r | \
        head -1 | \
        awk '{print $4}')

    if [ -z "$latest" ]; then
        error "No backups found in S3"
        exit 1
    fi

    local filename=$(basename "$latest")
    local local_path="$BACKUP_DIR/$filename"

    log "Downloading: $filename"
    mkdir -p "$BACKUP_DIR"

    if aws s3 cp "s3://${s3_bucket}/${latest}" "$local_path"; then
        log "Downloaded successfully: $local_path"
        echo "$local_path"
    else
        error "Failed to download backup from S3"
        exit 1
    fi
}

stop_application() {
    if [ "$STOP_SERVICES" != "true" ]; then
        log "Skipping service stop (--no-stop flag)"
        return 0
    fi

    log "Stopping application services..."

    if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
        if $DOCKER_COMPOSE stop api celery_worker 2>&1 | tee -a "$LOG_FILE"; then
            log "Services stopped successfully ✓"
            return 0
        else
            error "Failed to stop services"
            return 1
        fi
    else
        log "Docker Compose file not found, skipping service stop"
        return 0
    fi
}

start_application() {
    if [ "$STOP_SERVICES" != "true" ]; then
        return 0
    fi

    log "Starting application services..."

    if [ -f "docker-compose.yml" ] || [ -f "compose.yml" ]; then
        if $DOCKER_COMPOSE up -d api celery_worker 2>&1 | tee -a "$LOG_FILE"; then
            log "Services started successfully ✓"
            return 0
        else
            error "Failed to start services"
            return 1
        fi
    else
        log "Docker Compose file not found, skipping service start"
        return 0
    fi
}

verify_backup_file() {
    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        exit 1
    fi

    if [ ! -r "$backup_file" ]; then
        error "Backup file not readable: $backup_file"
        exit 1
    fi

    log "Verifying backup file..."

    if command -v pg_restore >/dev/null 2>&1; then
        if pg_restore --list "$backup_file" >/dev/null 2>&1; then
            log "Backup file verified ✓"
            return 0
        else
            error "Backup file appears to be corrupted"
            exit 1
        fi
    else
        error "pg_restore not found. Please install PostgreSQL client tools."
        exit 1
    fi
}

confirm_restore() {
    local backup_file="$1"

    cat <<EOF

⚠️  WARNING: DATABASE RESTORE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This operation will:
  1. Stop the application (api, celery_worker)
  2. DROP the current database: $DB_NAME
  3. Restore from backup: $(basename "$backup_file")
  4. Restart the application

⚠️  ALL CURRENT DATA WILL BE PERMANENTLY LOST!

Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}
Backup:   $backup_file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

    read -p "Type 'yes' to confirm restore: " confirm

    if [ "$confirm" != "yes" ]; then
        log "Restore cancelled by user"
        exit 0
    fi

    log "Restore confirmed by user"
}

perform_restore() {
    local backup_file="$1"

    log "Dropping existing database..."

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Drop database (ignore errors if doesn't exist)
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>&1 | tee -a "$LOG_FILE" || true

    # Create database
    log "Creating new database..."
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -c "CREATE DATABASE $DB_NAME;" 2>&1 | tee -a "$LOG_FILE"; then
        log "Database created successfully ✓"
    else
        error "Failed to create database"
        exit 1
    fi

    # Restore backup
    log "Restoring from backup..."
    log "This may take several minutes depending on backup size..."

    if pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-owner \
        --no-acl \
        "$backup_file" 2>&1 | tee -a "$LOG_FILE"; then
        log "Restore completed successfully ✓"
    else
        error "Restore failed (some errors may be expected)"
        # Don't exit - partial restore might be usable
    fi

    unset PGPASSWORD
}

verify_restore() {
    log "Verifying restored database..."

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Check if database exists
    local db_exists=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null || echo "")

    if [ "$db_exists" != "1" ]; then
        error "Database does not exist after restore"
        return 1
    fi

    # Count tables
    local table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")

    log "Tables restored: $table_count"

    if [ "$table_count" -eq 0 ]; then
        error "No tables found in restored database"
        return 1
    fi

    # Count users
    local user_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -tAc "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")

    log "Users found: $user_count"

    unset PGPASSWORD

    log "Database verification completed ✓"
}

# ============================================================================
# Main
# ============================================================================

main() {
    local backup_file=""
    local skip_confirm=false

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                usage
                ;;
            --list-backups)
                list_backups
                ;;
            --download-s3)
                backup_file=$(download_from_s3)
                ;;
            --no-stop)
                STOP_SERVICES=false
                ;;
            --no-confirm)
                skip_confirm=true
                ;;
            -*)
                error "Unknown option: $1"
                usage
                ;;
            *)
                if [ -z "$backup_file" ]; then
                    backup_file="$1"
                else
                    error "Too many arguments"
                    usage
                fi
                ;;
        esac
        shift
    done

    # Check if backup file specified
    if [ -z "$backup_file" ]; then
        error "No backup file specified"
        usage
    fi

    log "=========================================="
    log "Starting database restore"
    log "=========================================="
    log "Backup file: $backup_file"
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

    # Verify backup file
    verify_backup_file "$backup_file"

    # Confirm restore
    if [ "$skip_confirm" != "true" ]; then
        confirm_restore "$backup_file"
    else
        log "⚠️  Skipping confirmation (--no-confirm flag)"
    fi

    # Stop application
    stop_application

    # Perform restore
    perform_restore "$backup_file"

    # Verify restore
    verify_restore

    # Start application
    start_application

    # Summary
    log "=========================================="
    log "Restore completed successfully"
    log "=========================================="
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log "Restored from: $backup_file"
    log ""
    log "✓ Application should now be running with restored data"
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"

exit 0
