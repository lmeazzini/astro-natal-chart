#!/bin/bash
# Database Backup Script for Astro Application
# Performs full PostgreSQL backup with compression and optional S3 upload
# Author: Astro DevOps Team
# Version: 1.0.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Backup directory (will be created if doesn't exist)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# Timestamp format for backup files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_ONLY=$(date +"%Y%m%d")

# Backup filename
BACKUP_FILE="astro_backup_${TIMESTAMP}.sql.gz"

# Retention period (days)
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Database configuration (from environment or defaults)
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-astro}"
DB_USER="${DB_USER:-astro_user}"
DB_PASSWORD="${DB_PASSWORD:-}"

# S3 configuration (optional - for offsite backups)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
S3_PREFIX="${BACKUP_S3_PREFIX:-backups}"

# Healthcheck URL (optional - for monitoring)
HEALTHCHECK_URL="${BACKUP_HEALTHCHECK_URL:-}"

# Compression level (1-9, 9 is maximum)
COMPRESSION_LEVEL=9

# Log file
LOG_FILE="${BACKUP_LOG_FILE:-/var/log/astro-backup.log}"

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
}

cleanup_old_backups() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."

    if [ -d "$BACKUP_DIR" ]; then
        # Count backups before cleanup
        OLD_COUNT=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f | wc -l)

        # Remove old backups
        find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete

        # Count backups after cleanup
        NEW_COUNT=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f | wc -l)

        REMOVED=$((OLD_COUNT - NEW_COUNT))
        log "Removed $REMOVED old backup(s), kept $NEW_COUNT backup(s)"
    fi
}

verify_backup() {
    local backup_path="$1"

    log "Verifying backup integrity..."

    # Check if file exists and is readable
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

    # Verify pg_dump format
    if command -v pg_restore >/dev/null 2>&1; then
        if pg_restore --list "$backup_path" >/dev/null 2>&1; then
            log "Backup integrity verified ✓ (size: $(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B))"
            return 0
        else
            error "Backup integrity check failed - pg_restore cannot read the file"
            return 1
        fi
    else
        log "pg_restore not available, skipping detailed verification (size: $(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B))"
        return 0
    fi
}

upload_to_s3() {
    local backup_path="$1"

    if [ -z "$S3_BUCKET" ]; then
        log "S3 upload skipped (S3_BUCKET not configured)"
        return 0
    fi

    log "Uploading backup to S3..."

    if command -v aws >/dev/null 2>&1; then
        local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${DATE_ONLY}/${BACKUP_FILE}"

        if aws s3 cp "$backup_path" "$s3_path"; then
            log "Backup uploaded to S3: $s3_path ✓"
            return 0
        else
            error "Failed to upload backup to S3"
            return 1
        fi
    else
        error "AWS CLI not installed, cannot upload to S3"
        return 1
    fi
}

send_healthcheck() {
    if [ -z "$HEALTHCHECK_URL" ]; then
        return 0
    fi

    log "Sending healthcheck ping..."

    if command -v curl >/dev/null 2>&1; then
        if curl -fsS --retry 3 --max-time 10 "$HEALTHCHECK_URL" >/dev/null 2>&1; then
            log "Healthcheck ping sent ✓"
        else
            error "Failed to send healthcheck ping"
        fi
    fi
}

check_disk_space() {
    local required_mb=100  # Minimum 100MB free space

    if command -v df >/dev/null 2>&1; then
        local available_mb=$(df -BM "$BACKUP_DIR" 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/M//')

        if [ -n "$available_mb" ] && [ "$available_mb" -lt "$required_mb" ]; then
            error "Insufficient disk space: ${available_mb}MB available, ${required_mb}MB required"
            return 1
        fi

        log "Disk space check passed: ${available_mb}MB available"
    fi

    return 0
}

# ============================================================================
# Main Backup Process
# ============================================================================

main() {
    log "=========================================="
    log "Starting database backup"
    log "=========================================="
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log "Backup file: ${BACKUP_FILE}"
    log "Retention: ${RETENTION_DAYS} days"

    # Check prerequisites
    if ! command -v pg_dump >/dev/null 2>&1; then
        error "pg_dump not found. Please install PostgreSQL client tools."
        exit 1
    fi

    # Check disk space
    if ! check_disk_space; then
        error "Pre-backup disk space check failed"
        exit 1
    fi

    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    log "Backup directory: $BACKUP_DIR"

    # Create backup
    log "Creating compressed backup..."
    local backup_path="$BACKUP_DIR/$BACKUP_FILE"

    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    if pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --format=custom \
        --compress="$COMPRESSION_LEVEL" \
        --verbose \
        --file="$backup_path" 2>&1 | tee -a "$LOG_FILE"; then
        log "Backup created successfully: $BACKUP_FILE ✓"
    else
        error "Backup creation failed"
        exit 1
    fi

    unset PGPASSWORD

    # Verify backup integrity
    if ! verify_backup "$backup_path"; then
        error "Backup verification failed"
        exit 1
    fi

    # Upload to S3 (offsite)
    upload_to_s3 "$backup_path"

    # Cleanup old backups
    cleanup_old_backups

    # Send healthcheck ping
    send_healthcheck

    # Summary
    log "=========================================="
    log "Backup completed successfully"
    log "=========================================="
    log "Backup file: $backup_path"
    log "Next backup: $(date -d '+1 day' +'%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v+1d +'%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'tomorrow')"
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main

exit 0
