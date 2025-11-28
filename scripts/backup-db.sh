#!/bin/bash
# Database Backup Script for Astro Application
# Performs full PostgreSQL backup with compression and optional S3 upload
# Also backs up Qdrant vector database snapshots
# Author: Astro DevOps Team
# Version: 1.2.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Script directory (for calling Python services)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Backup directory (will be created if doesn't exist)
BACKUP_DIR="${BACKUP_DIR:-/var/backups/astro-db}"

# Timestamp format for backup files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATE_ONLY=$(date +"%Y%m%d")

# Custom backup name (optional - use BACKUP_NAME env var for named backups like "initial")
BACKUP_NAME="${BACKUP_NAME:-${TIMESTAMP}}"

# Backup filename
BACKUP_FILE="astro_backup_${BACKUP_NAME}.sql.gz"

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

# Qdrant configuration
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_COLLECTION="${QDRANT_COLLECTION:-astrology_knowledge}"
QDRANT_BACKUP_FILE="qdrant_backup_${BACKUP_NAME}.snapshot"

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

        # Remove old metadata files
        find "$BACKUP_DIR" -name "astro_backup_*.sql.gz.meta" -type f -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true

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

    if [ -z "$BACKUP_S3_BUCKET" ]; then
        log "S3 upload skipped (BACKUP_S3_BUCKET not configured)"
        return 0
    fi

    log "Uploading backup to S3 using BackupS3Service..."

    # Call Python BackupS3Service with retry and integrity verification
    local result
    result=$(cd "${SCRIPT_DIR}/.." && uv run python -c "
import sys
from pathlib import Path
from app.services.backup_s3_service import backup_s3_service

try:
    s3_url = backup_s3_service.upload_backup(Path('$backup_path'))
    if s3_url:
        print(f'SUCCESS:{s3_url}')
        sys.exit(0)
    else:
        print('FAILED:Upload returned None')
        sys.exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
" 2>&1)

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        local s3_url=$(echo "$result" | grep '^SUCCESS:' | cut -d: -f2-)
        log "Backup uploaded to S3: $s3_url ✓"
        log "Uploaded with retry logic (3 attempts) and MD5 verification"
        return 0
    else
        error "S3 upload failed: $result"
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

create_backup_metadata() {
    local backup_path="$1"
    local metadata_file="${backup_path}.meta"

    log "Creating backup metadata file..."

    # Get PostgreSQL version
    local pg_version=""
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    pg_version=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version()" 2>/dev/null | head -n1 | xargs)

    unset PGPASSWORD

    # Get backup file size
    local file_size=$(stat -c%s "$backup_path" 2>/dev/null || stat -f%z "$backup_path" 2>/dev/null)
    local file_size_human=$(numfmt --to=iec-i --suffix=B "$file_size" 2>/dev/null || echo "${file_size}B")

    # Get database size
    local db_size=""
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi

    db_size=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'))" 2>/dev/null | xargs)

    unset PGPASSWORD

    # Write metadata in JSON format
    cat > "$metadata_file" <<EOF
{
  "backup_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "backup_file": "$BACKUP_FILE",
  "backup_size_bytes": $file_size,
  "backup_size_human": "$file_size_human",
  "database": {
    "name": "$DB_NAME",
    "host": "$DB_HOST",
    "port": $DB_PORT,
    "version": "$pg_version",
    "size": "$db_size"
  },
  "retention_days": $RETENTION_DAYS,
  "compression_level": $COMPRESSION_LEVEL,
  "script_version": "1.2.0",
  "hostname": "$(hostname 2>/dev/null || echo 'unknown')"
}
EOF

    if [ -f "$metadata_file" ]; then
        log "Backup metadata created: ${BACKUP_FILE}.meta ✓"
        return 0
    else
        error "Failed to create metadata file"
        return 1
    fi
}

backup_qdrant() {
    log "Starting Qdrant vector database backup..."

    local qdrant_url="http://${QDRANT_HOST}:${QDRANT_PORT}"
    local qdrant_backup_path="$BACKUP_DIR/$QDRANT_BACKUP_FILE"

    # Check if Qdrant is reachable
    if ! curl -sf "${qdrant_url}/healthz" >/dev/null 2>&1; then
        log "Qdrant not reachable at ${qdrant_url}, skipping Qdrant backup"
        return 0
    fi

    # Check if collection exists
    local collection_info
    collection_info=$(curl -sf "${qdrant_url}/collections/${QDRANT_COLLECTION}" 2>/dev/null)
    if [ -z "$collection_info" ]; then
        log "Qdrant collection '${QDRANT_COLLECTION}' not found, skipping Qdrant backup"
        return 0
    fi

    local points_count
    points_count=$(echo "$collection_info" | grep -o '"points_count":[0-9]*' | cut -d: -f2)
    log "Qdrant collection '${QDRANT_COLLECTION}' has ${points_count:-0} vectors"

    # Create snapshot via Qdrant API
    log "Creating Qdrant snapshot..."
    local snapshot_response
    snapshot_response=$(curl -sf -X POST "${qdrant_url}/collections/${QDRANT_COLLECTION}/snapshots" 2>&1)

    if [ -z "$snapshot_response" ]; then
        error "Failed to create Qdrant snapshot"
        return 1
    fi

    # Extract snapshot name from response
    local snapshot_name
    snapshot_name=$(echo "$snapshot_response" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$snapshot_name" ]; then
        error "Could not extract snapshot name from Qdrant response: $snapshot_response"
        return 1
    fi

    log "Qdrant snapshot created: $snapshot_name"

    # Download the snapshot
    log "Downloading Qdrant snapshot..."
    local download_url="${qdrant_url}/collections/${QDRANT_COLLECTION}/snapshots/${snapshot_name}"

    if curl -sf -o "$qdrant_backup_path" "$download_url"; then
        local file_size=$(stat -c%s "$qdrant_backup_path" 2>/dev/null || stat -f%z "$qdrant_backup_path" 2>/dev/null)
        log "Qdrant snapshot downloaded: $QDRANT_BACKUP_FILE ($(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B)) ✓"
    else
        error "Failed to download Qdrant snapshot"
        return 1
    fi

    # Clean up old Qdrant snapshots on server (keep last 3)
    log "Cleaning up old Qdrant snapshots on server..."
    local snapshots_list
    snapshots_list=$(curl -sf "${qdrant_url}/collections/${QDRANT_COLLECTION}/snapshots" 2>/dev/null)

    if [ -n "$snapshots_list" ]; then
        # Get all snapshot names except the latest 3
        local old_snapshots
        old_snapshots=$(echo "$snapshots_list" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sort -r | tail -n +4)

        for old_snap in $old_snapshots; do
            log "Deleting old Qdrant snapshot: $old_snap"
            curl -sf -X DELETE "${qdrant_url}/collections/${QDRANT_COLLECTION}/snapshots/${old_snap}" >/dev/null 2>&1 || true
        done
    fi

    # Clean up old local Qdrant backups
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "qdrant_backup_*.snapshot" -type f -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
    fi

    log "Qdrant backup completed successfully ✓"
    return 0
}

upload_qdrant_to_s3() {
    local qdrant_backup_path="$BACKUP_DIR/$QDRANT_BACKUP_FILE"

    if [ ! -f "$qdrant_backup_path" ]; then
        log "No Qdrant backup file to upload"
        return 0
    fi

    if [ -z "$BACKUP_S3_BUCKET" ]; then
        log "S3 upload for Qdrant skipped (BACKUP_S3_BUCKET not configured)"
        return 0
    fi

    log "Uploading Qdrant backup to S3..."

    # Use aws cli or Python service
    if command -v aws >/dev/null 2>&1; then
        local s3_key="${S3_PREFIX}/qdrant/${QDRANT_BACKUP_FILE}"
        if aws s3 cp "$qdrant_backup_path" "s3://${BACKUP_S3_BUCKET}/${s3_key}" --quiet; then
            log "Qdrant backup uploaded to S3: s3://${BACKUP_S3_BUCKET}/${s3_key} ✓"
            return 0
        else
            error "Failed to upload Qdrant backup to S3"
            return 1
        fi
    else
        log "AWS CLI not available, skipping Qdrant S3 upload"
        return 0
    fi
}

# ============================================================================
# Main Backup Process
# ============================================================================

main() {
    log "=========================================="
    log "Starting database backup (PostgreSQL + Qdrant)"
    log "=========================================="
    log "PostgreSQL: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log "Qdrant: ${QDRANT_HOST}:${QDRANT_PORT} (collection: ${QDRANT_COLLECTION})"
    log "PostgreSQL backup file: ${BACKUP_FILE}"
    log "Qdrant backup file: ${QDRANT_BACKUP_FILE}"
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

    # Create backup metadata file
    create_backup_metadata "$backup_path"

    # Upload PostgreSQL backup to S3 (offsite)
    upload_to_s3 "$backup_path"

    # Cleanup old PostgreSQL backups
    cleanup_old_backups

    # ==========================================
    # Qdrant Vector Database Backup
    # ==========================================
    log ""
    log "=========================================="
    log "Starting Qdrant vector database backup"
    log "=========================================="

    # Backup Qdrant
    if backup_qdrant; then
        # Upload Qdrant backup to S3
        upload_qdrant_to_s3
    else
        log "Qdrant backup skipped or failed (non-fatal)"
    fi

    # Send healthcheck ping
    send_healthcheck

    # Summary
    log ""
    log "=========================================="
    log "All backups completed successfully"
    log "=========================================="
    log "PostgreSQL backup: $backup_path"
    if [ -f "$BACKUP_DIR/$QDRANT_BACKUP_FILE" ]; then
        log "Qdrant backup: $BACKUP_DIR/$QDRANT_BACKUP_FILE"
    fi
    log "Next backup: $(date -d '+1 day' +'%Y-%m-%d %H:%M:%S' 2>/dev/null || date -v+1d +'%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'tomorrow')"
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
# Use temp log if we don't have permission to write to default location
if ! mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || ! touch "$LOG_FILE" 2>/dev/null; then
    LOG_FILE="/tmp/astro-backup-$(date +%Y%m%d-%H%M%S).log"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: Cannot write to default log location, using: $LOG_FILE" >&2
fi

# Run main function
main

exit 0
