#!/bin/bash
# Backup Verification Script for Astro Application
# Monitors backup health and sends alerts if issues detected
# Author: Astro DevOps Team
# Version: 1.0.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Backup directory
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# Maximum backup age in hours
MAX_BACKUP_AGE_HOURS="${MAX_BACKUP_AGE_HOURS:-26}"

# Minimum backup size in bytes (100KB)
MIN_BACKUP_SIZE="${MIN_BACKUP_SIZE:-102400}"

# Required minimum number of backups
MIN_BACKUP_COUNT="${MIN_BACKUP_COUNT:-7}"

# S3 configuration (optional)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
S3_PREFIX="${BACKUP_S3_PREFIX:-backups}"

# Healthcheck URL (send alert on failure)
HEALTHCHECK_FAIL_URL="${BACKUP_HEALTHCHECK_FAIL_URL:-}"

# Log file
LOG_FILE="${BACKUP_VERIFY_LOG_FILE:-/var/log/astro-backup-verify.log}"

# Exit code
EXIT_CODE=0

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*" | tee -a "$LOG_FILE" >&2
    EXIT_CODE=1
}

warn() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"

    # Send to healthcheck URL if configured
    if [ -n "$HEALTHCHECK_FAIL_URL" ]; then
        if command -v curl >/dev/null 2>&1; then
            curl -fsS --retry 3 --max-time 10 \
                --data-raw "$message" \
                "$HEALTHCHECK_FAIL_URL" >/dev/null 2>&1 || true
        fi
    fi

    # Could also send email, Slack notification, etc.
}

check_backup_directory() {
    log "Checking backup directory..."

    if [ ! -d "$BACKUP_DIR" ]; then
        error "Backup directory does not exist: $BACKUP_DIR"
        return 1
    fi

    if [ ! -r "$BACKUP_DIR" ]; then
        error "Backup directory not readable: $BACKUP_DIR"
        return 1
    fi

    log "✓ Backup directory exists and is readable"
    return 0
}

check_latest_backup_age() {
    log "Checking latest backup age..."

    local latest=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | sort -r | head -1)

    if [ -z "$latest" ]; then
        error "No backups found in $BACKUP_DIR"
        send_alert "CRITICAL: No backups found in $BACKUP_DIR"
        return 1
    fi

    local backup_name=$(basename "$latest")

    # Get file modification time (cross-platform)
    local file_time=$(stat -c %Y "$latest" 2>/dev/null || stat -f %m "$latest" 2>/dev/null)
    local current_time=$(date +%s)
    local age_seconds=$((current_time - file_time))
    local age_hours=$((age_seconds / 3600))
    local age_minutes=$(((age_seconds % 3600) / 60))

    log "Latest backup: $backup_name"
    log "Backup age: ${age_hours}h ${age_minutes}m"

    if [ "$age_hours" -gt "$MAX_BACKUP_AGE_HOURS" ]; then
        error "Latest backup is too old: ${age_hours}h (max: ${MAX_BACKUP_AGE_HOURS}h)"
        send_alert "CRITICAL: Latest backup is ${age_hours}h old (max: ${MAX_BACKUP_AGE_HOURS}h)"
        return 1
    fi

    log "✓ Latest backup age is acceptable"
    return 0
}

check_backup_count() {
    log "Checking backup count..."

    local backup_count=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | wc -l)

    log "Backups found: $backup_count"

    if [ "$backup_count" -lt "$MIN_BACKUP_COUNT" ]; then
        warn "Backup count is below recommended minimum: $backup_count (min: $MIN_BACKUP_COUNT)"
        return 1
    fi

    log "✓ Backup count is sufficient"
    return 0
}

check_backup_sizes() {
    log "Checking backup file sizes..."

    local backups=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null)

    if [ -z "$backups" ]; then
        error "No backups found"
        return 1
    fi

    local issues=0

    echo "$backups" | while read -r backup; do
        local size=$(stat -c%s "$backup" 2>/dev/null || stat -f%z "$backup" 2>/dev/null)
        local size_mb=$((size / 1024 / 1024))

        if [ "$size" -lt "$MIN_BACKUP_SIZE" ]; then
            error "Backup file too small: $(basename "$backup") (${size_mb}MB)"
            issues=$((issues + 1))
        fi
    done

    if [ "$issues" -eq 0 ]; then
        log "✓ All backup files have acceptable sizes"
        return 0
    fi

    return 1
}

check_backup_integrity() {
    log "Checking backup file integrity..."

    local latest=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | sort -r | head -1)

    if [ -z "$latest" ]; then
        error "No backups found to verify"
        return 1
    fi

    local backup_name=$(basename "$latest")

    if command -v pg_restore >/dev/null 2>&1; then
        if pg_restore --list "$latest" >/dev/null 2>&1; then
            log "✓ Latest backup integrity verified: $backup_name"
            return 0
        else
            error "Backup integrity check failed: $backup_name"
            send_alert "CRITICAL: Backup integrity check failed for $backup_name"
            return 1
        fi
    else
        warn "pg_restore not available, skipping integrity check"
        return 0
    fi
}

check_disk_space() {
    log "Checking disk space..."

    if ! command -v df >/dev/null 2>&1; then
        warn "df command not available, skipping disk space check"
        return 0
    fi

    local available_mb=$(df -BM "$BACKUP_DIR" 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/M//')

    if [ -z "$available_mb" ]; then
        warn "Could not determine available disk space"
        return 0
    fi

    log "Available disk space: ${available_mb}MB"

    # Warn if less than 500MB available
    if [ "$available_mb" -lt 500 ]; then
        warn "Low disk space: ${available_mb}MB available"
        return 1
    fi

    # Critical if less than 100MB available
    if [ "$available_mb" -lt 100 ]; then
        error "Critical disk space: ${available_mb}MB available"
        send_alert "CRITICAL: Low disk space for backups: ${available_mb}MB"
        return 1
    fi

    log "✓ Sufficient disk space available"
    return 0
}

check_s3_backups() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 backups not configured, skipping check"
        return 0
    fi

    log "Checking S3 backups..."

    if ! command -v aws >/dev/null 2>&1; then
        warn "AWS CLI not installed, cannot check S3 backups"
        return 0
    fi

    # List recent S3 backups
    local s3_backup_count=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --recursive 2>/dev/null | \
        grep "astro_backup_.*\.sql\.gz$" | wc -l || echo "0")

    log "S3 backups found: $s3_backup_count"

    if [ "$s3_backup_count" -eq 0 ]; then
        error "No backups found in S3"
        return 1
    fi

    # Check latest S3 backup age
    local latest_s3=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --recursive 2>/dev/null | \
        grep "astro_backup_.*\.sql\.gz$" | \
        sort -r | head -1)

    if [ -n "$latest_s3" ]; then
        local s3_date=$(echo "$latest_s3" | awk '{print $1" "$2}')
        log "Latest S3 backup: $s3_date"
        log "✓ S3 backups are available"
    fi

    return 0
}

generate_report() {
    log "=========================================="
    log "Backup Verification Summary"
    log "=========================================="

    # Count backups
    local local_backups=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | wc -l)

    # Get latest backup info
    local latest=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | sort -r | head -1)

    if [ -n "$latest" ]; then
        local file_time=$(stat -c %Y "$latest" 2>/dev/null || stat -f %m "$latest" 2>/dev/null)
        local current_time=$(date +%s)
        local age_hours=$(((current_time - file_time) / 3600))
        local size=$(stat -c%s "$latest" 2>/dev/null || stat -f%z "$latest" 2>/dev/null)
        local size_mb=$((size / 1024 / 1024))

        log "Local backups: $local_backups"
        log "Latest backup: $(basename "$latest")"
        log "Backup age: ${age_hours}h"
        log "Backup size: ${size_mb}MB"
    else
        log "Local backups: 0"
        log "Latest backup: NONE"
    fi

    # Disk space
    if command -v df >/dev/null 2>&1; then
        local available=$(df -BM "$BACKUP_DIR" 2>/dev/null | awk 'NR==2 {print $4}')
        log "Available space: $available"
    fi

    log "=========================================="

    if [ "$EXIT_CODE" -eq 0 ]; then
        log "Status: ✓ ALL CHECKS PASSED"
    else
        log "Status: ✗ CHECKS FAILED"
    fi

    log "=========================================="
}

# ============================================================================
# Main
# ============================================================================

main() {
    log "=========================================="
    log "Starting backup verification"
    log "=========================================="
    log "Backup directory: $BACKUP_DIR"
    log "Max age: ${MAX_BACKUP_AGE_HOURS}h"
    log "Min count: $MIN_BACKUP_COUNT"

    # Run checks
    check_backup_directory || true
    check_latest_backup_age || true
    check_backup_count || true
    check_backup_sizes || true
    check_backup_integrity || true
    check_disk_space || true
    check_s3_backups || true

    # Generate report
    generate_report

    exit $EXIT_CODE
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"

exit $EXIT_CODE
