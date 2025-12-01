#!/bin/bash
# Database Restore Script for Astro Application
# Restores PostgreSQL database from backup with safety checks
# Author: Astro DevOps Team
# Version: 1.0.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# Timestamp for pre-restore backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database configuration (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-astro}"
DB_USER="${DB_USER:-astro_user}"
DB_PASSWORD="${DB_PASSWORD:-}"

# S3 configuration (from environment)
BACKUP_S3_BUCKET="${BACKUP_S3_BUCKET:-}"
BACKUP_S3_PREFIX="${BACKUP_S3_PREFIX:-backups}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Log file
LOG_FILE="${RESTORE_LOG_FILE:-/var/log/astro-restore.log}"

# Flags
DRY_RUN=false
SKIP_BACKUP=false
SKIP_SERVICES=false
CONFIRMED=false
BACKUP_FILE=""
FROM_S3=false
FROM_S3_LATEST=false
S3_URL=""
LIST_S3=false

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*" | tee -a "$LOG_FILE"
}

show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Restore PostgreSQL database from backup file with safety checks.

Backup Source (choose one):
  --backup-file PATH       Path to local backup file
  --from-s3-latest         Download and restore latest backup from S3
  --from-s3 S3_URL         Download and restore specific S3 backup
  --list-s3                List available backups in S3 and exit

Options:
  --dry-run                Validate backup but don't restore
  --skip-backup            Skip pre-restore backup (DANGEROUS)
  --skip-services          Don't stop/start Docker services
  --confirm                Skip confirmation prompt (for automation)
  -h, --help               Show this help message

Examples:
  # Restore from local file (interactive)
  $0 --backup-file /var/backups/astro-db/astro_backup_20250125_120000.sql.gz

  # Restore latest backup from S3
  $0 --from-s3-latest

  # Restore specific backup from S3
  $0 --from-s3 s3://genesis-559050210551-backup-dev/backups/20250128/astro_backup_20250128_030000.sql.gz

  # List available S3 backups
  $0 --list-s3

  # Automated restore with latest S3 backup (CI/CD)
  $0 --from-s3-latest --confirm

  # Dry run to validate S3 backup
  $0 --from-s3-latest --dry-run

Environment Variables:
  DB_HOST                Database host (default: localhost)
  DB_PORT                Database port (default: 5432)
  DB_NAME                Database name (default: astro)
  DB_USER                Database user (default: astro_user)
  DB_PASSWORD            Database password
  BACKUP_DIR             Backup directory (default: /var/backups/astro-db)
  BACKUP_S3_BUCKET       S3 bucket for backups
  BACKUP_S3_PREFIX       S3 prefix (default: backups)
  AWS_REGION             AWS region (default: us-east-1)
  RESTORE_LOG_FILE       Log file path (default: /var/log/astro-restore.log)

EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup-file)
                BACKUP_FILE="$2"
                shift 2
                ;;
            --from-s3-latest)
                FROM_S3_LATEST=true
                FROM_S3=true
                shift
                ;;
            --from-s3)
                S3_URL="$2"
                FROM_S3=true
                shift 2
                ;;
            --list-s3)
                LIST_S3=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-services)
                SKIP_SERVICES=true
                shift
                ;;
            --confirm)
                CONFIRMED=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Validation: need at least one backup source (unless --list-s3)
    if [ "$LIST_S3" = false ] && [ -z "$BACKUP_FILE" ] && [ "$FROM_S3" = false ]; then
        error "Missing backup source. Use --backup-file, --from-s3-latest, or --from-s3"
        show_usage
        exit 1
    fi

    # Validation: cannot use both local file and S3
    if [ -n "$BACKUP_FILE" ] && [ "$FROM_S3" = true ]; then
        error "Cannot use both --backup-file and S3 options. Choose one."
        show_usage
        exit 1
    fi
}

check_s3_configured() {
    if [ -z "$BACKUP_S3_BUCKET" ]; then
        error "S3 not configured. Set BACKUP_S3_BUCKET environment variable."
        return 1
    fi

    if ! command -v aws >/dev/null 2>&1; then
        error "AWS CLI not found. Please install: https://aws.amazon.com/cli/"
        return 1
    fi

    # Test AWS credentials
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        error "AWS credentials not configured or invalid"
        error "Run: aws configure"
        return 1
    fi

    return 0
}

list_s3_backups() {
    log "Listing backups in S3 bucket: s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}/"

    if ! check_s3_configured; then
        return 1
    fi

    # List objects in S3
    local backups
    backups=$(aws s3 ls "s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}/" \
        --recursive \
        --region "$AWS_REGION" \
        --human-readable \
        --summarize 2>&1)

    if [ $? -ne 0 ]; then
        error "Failed to list S3 backups"
        echo "$backups" >&2
        return 1
    fi

    echo "$backups" | grep ".sql.gz$"

    return 0
}

get_latest_s3_backup() {
    log "Finding latest backup in S3..."

    if ! check_s3_configured; then
        return 1
    fi

    # Get latest backup URL
    local latest_backup
    latest_backup=$(aws s3 ls "s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}/" \
        --recursive \
        --region "$AWS_REGION" 2>&1 | \
        grep ".sql.gz$" | \
        sort -r | \
        head -n 1 | \
        awk '{print $4}')

    if [ -z "$latest_backup" ]; then
        error "No backups found in S3"
        return 1
    fi

    # Return full S3 URL
    echo "s3://${BACKUP_S3_BUCKET}/${latest_backup}"
    return 0
}

download_from_s3() {
    local s3_url="$1"
    local local_path="$2"

    log "Downloading backup from S3..."
    log "Source: $s3_url"
    log "Destination: $local_path"

    if ! check_s3_configured; then
        return 1
    fi

    # Create parent directory if needed
    mkdir -p "$(dirname "$local_path")"

    # Download with AWS CLI
    if aws s3 cp "$s3_url" "$local_path" --region "$AWS_REGION" 2>&1 | tee -a "$LOG_FILE"; then
        log "Download completed successfully ✓"
        return 0
    else
        error "Failed to download backup from S3"
        return 1
    fi
}

validate_backup() {
    local backup_path="$1"

    log "Validating backup file..."

    # Check if file exists
    if [ ! -f "$backup_path" ]; then
        error "Backup file not found: $backup_path"
        return 1
    fi

    # Check if file is readable
    if [ ! -r "$backup_path" ]; then
        error "Backup file not readable: $backup_path"
        return 1
    fi

    # Check file size (should be > 1KB)
    local file_size=$(stat -c%s "$backup_path" 2>/dev/null || stat -f%z "$backup_path" 2>/dev/null)
    if [ "$file_size" -lt 1024 ]; then
        error "Backup file too small (${file_size} bytes), likely corrupted"
        return 1
    fi

    # Verify pg_dump format using pg_restore --list
    if ! command -v pg_restore >/dev/null 2>&1; then
        error "pg_restore not found. Please install PostgreSQL client tools."
        return 1
    fi

    if ! pg_restore --list "$backup_path" >/dev/null 2>&1; then
        error "Backup integrity check failed - pg_restore cannot read the file"
        return 1
    fi

    log "Backup validation passed ✓ (size: $(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B))"
    return 0
}

create_pre_restore_backup() {
    log "Creating pre-restore backup of current database..."

    local pre_restore_backup="$BACKUP_DIR/pre_restore_${TIMESTAMP}.sql.gz"

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    if pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --file="$pre_restore_backup" 2>&1 | tee -a "$LOG_FILE"; then
        log "Pre-restore backup created: $pre_restore_backup ✓"
        log "You can restore this backup if the restore operation fails"
    else
        error "Pre-restore backup failed"
        return 1
    fi

    unset PGPASSWORD
    return 0
}

stop_services() {
    if [ "$SKIP_SERVICES" = true ]; then
        log "Skipping service stop (--skip-services flag)"
        return 0
    fi

    log "Stopping dependent services (API, Celery)..."

    # Check if docker-compose is available
    if command -v docker-compose >/dev/null 2>&1; then
        cd "${SCRIPT_DIR}/.." || exit 1

        # Stop API and Celery (keep db and redis running)
        docker-compose stop api celery_worker web 2>&1 | tee -a "$LOG_FILE" || true

        log "Services stopped ✓"
    else
        warn "docker-compose not found, skipping service stop"
    fi

    return 0
}

start_services() {
    if [ "$SKIP_SERVICES" = true ]; then
        log "Skipping service start (--skip-services flag)"
        return 0
    fi

    log "Starting services..."

    if command -v docker-compose >/dev/null 2>&1; then
        cd "${SCRIPT_DIR}/.." || exit 1

        # Start services
        docker-compose up -d api celery_worker web 2>&1 | tee -a "$LOG_FILE" || true

        log "Services started ✓"
    else
        warn "docker-compose not found, skipping service start"
    fi

    return 0
}

restore_database() {
    local backup_path="$1"

    log "Restoring database from backup..."
    log "WARNING: This will REPLACE all data in ${DB_NAME}!"

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Drop existing connections (PostgreSQL)
    log "Terminating existing connections..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
        -v dbname="$DB_NAME" <<-EOSQL 2>&1 | tee -a "$LOG_FILE" || true
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = :'dbname' AND pid <> pg_backend_pid();
EOSQL

    # Restore using pg_restore
    log "Running pg_restore..."
    if pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --clean \
        --if-exists \
        --no-owner \
        --no-acl \
        --verbose \
        "$backup_path" 2>&1 | tee -a "$LOG_FILE"; then
        log "Database restore completed successfully ✓"
    else
        error "Database restore failed (non-zero exit code)"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

validate_post_restore() {
    log "Validating database after restore..."

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    # Check if database is accessible
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" >/dev/null 2>&1; then
        error "Database not accessible after restore"
        unset PGPASSWORD
        return 1
    fi

    # Count tables
    local table_count
    table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'" 2>/dev/null | tr -d ' ')

    if [ -z "$table_count" ] || [ "$table_count" -lt 1 ]; then
        error "Database restore validation failed: no tables found"
        unset PGPASSWORD
        return 1
    fi

    log "Post-restore validation passed ✓ (${table_count} tables found)"

    # Count users (basic sanity check)
    local user_count
    user_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM users" 2>/dev/null | tr -d ' ') || user_count=0

    log "Users in database: ${user_count}"

    unset PGPASSWORD
    return 0
}

confirm_restore() {
    if [ "$CONFIRMED" = true ]; then
        log "Confirmation skipped (--confirm flag)"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        return 0
    fi

    cat <<EOF

========================================
  ⚠️  DANGER - DATABASE RESTORE  ⚠️
========================================

This will REPLACE all data in the database: $DB_NAME

Current database: ${DB_NAME}@${DB_HOST}:${DB_PORT}
Backup file: $BACKUP_FILE

Actions to be performed:
  1. Create pre-restore backup
  2. Stop API and Celery services
  3. Terminate all database connections
  4. Restore database from backup
  5. Validate restored data
  6. Restart services

EOF

    if [ "$SKIP_BACKUP" = true ]; then
        warn "Pre-restore backup will be SKIPPED (--skip-backup flag)"
    fi

    read -p "Are you sure you want to continue? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        exit 0
    fi

    log "Restore confirmed by user"
    return 0
}

# ============================================================================
# Main Restore Process
# ============================================================================

main() {
    log "=========================================="
    log "Starting database restore"
    log "=========================================="
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"

    # Handle --list-s3 flag (list and exit)
    if [ "$LIST_S3" = true ]; then
        list_s3_backups
        exit $?
    fi

    # Handle S3 restore
    if [ "$FROM_S3" = true ]; then
        log "S3 restore mode enabled"

        # Determine S3 URL
        if [ "$FROM_S3_LATEST" = true ]; then
            log "Getting latest backup from S3..."
            S3_URL=$(get_latest_s3_backup)
            if [ $? -ne 0 ]; then
                error "Failed to find latest S3 backup"
                exit 1
            fi
            log "Latest backup: $S3_URL"
        fi

        if [ -z "$S3_URL" ]; then
            error "No S3 URL provided or found"
            exit 1
        fi

        # Extract filename from S3 URL
        local backup_filename
        backup_filename=$(basename "$S3_URL")

        # Download to backup directory
        BACKUP_FILE="${BACKUP_DIR}/${backup_filename}"

        log "Downloading backup from S3..."
        if ! download_from_s3 "$S3_URL" "$BACKUP_FILE"; then
            error "Failed to download backup from S3"
            exit 1
        fi
    fi

    log "Backup file: $BACKUP_FILE"
    log "Dry run: $DRY_RUN"

    # Validate backup file
    if ! validate_backup "$BACKUP_FILE"; then
        error "Backup validation failed"
        exit 1
    fi

    if [ "$DRY_RUN" = true ]; then
        log ""
        log "=========================================="
        log "DRY RUN MODE - No changes made"
        log "=========================================="
        log "Backup file is valid and can be restored ✓"
        exit 0
    fi

    # Confirm with user
    confirm_restore

    # Create pre-restore backup
    if [ "$SKIP_BACKUP" = false ]; then
        if ! create_pre_restore_backup; then
            error "Pre-restore backup failed, aborting restore"
            exit 1
        fi
    else
        warn "Skipping pre-restore backup (--skip-backup flag)"
    fi

    # Stop services
    stop_services

    # Wait a bit for services to stop
    sleep 3

    # Restore database
    if ! restore_database "$BACKUP_FILE"; then
        error "Database restore failed!"
        error "You can restore the pre-restore backup: $BACKUP_DIR/pre_restore_${TIMESTAMP}.sql.gz"
        start_services
        exit 1
    fi

    # Validate restore
    if ! validate_post_restore; then
        error "Post-restore validation failed!"
        error "You can restore the pre-restore backup: $BACKUP_DIR/pre_restore_${TIMESTAMP}.sql.gz"
        start_services
        exit 1
    fi

    # Start services
    start_services

    # Summary
    log ""
    log "=========================================="
    log "Database restore completed successfully"
    log "=========================================="
    log "Restored from: $BACKUP_FILE"
    if [ "$SKIP_BACKUP" = false ]; then
        log "Pre-restore backup: $BACKUP_DIR/pre_restore_${TIMESTAMP}.sql.gz"
    fi
    log "Database is now ready for use"
}

# ============================================================================
# Execute
# ============================================================================

# Parse command line arguments
parse_args "$@"

# Create log file parent directory if it doesn't exist
# Use temp log if we don't have permission to write to default location
if ! mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || ! touch "$LOG_FILE" 2>/dev/null; then
    LOG_FILE="/tmp/astro-restore-$(date +%Y%m%d-%H%M%S).log"
    warn "Cannot write to default log location, using: $LOG_FILE"
fi

# Run main function
main

exit 0
