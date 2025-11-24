#!/bin/bash
# Database Restore Script for Astro Application
# Restores PostgreSQL database and Qdrant vector database from backup files
# Author: Astro DevOps Team
# Version: 1.1.0

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# ============================================================================
# Configuration
# ============================================================================

# Script directory (for calling Python services)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Qdrant configuration
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_COLLECTION="${QDRANT_COLLECTION:-astrology_knowledge}"

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

Restore PostgreSQL database and optionally Qdrant from backup files.

Arguments:
    backup_file         Path to PostgreSQL backup file (*.sql.gz) or S3 URL

Options:
    --no-stop           Don't stop application services
    --no-confirm        Skip confirmation prompt (dangerous!)
    --download-s3       Download latest backup from S3 first
    --list-backups      List available local backups
    --list-s3           List backups available in S3
    --qdrant FILE       Also restore Qdrant from snapshot file
    --skip-qdrant       Skip Qdrant restore even if snapshot exists
    --help              Show this help message

Environment Variables:
    DB_HOST             Database host (default: localhost)
    DB_PORT             Database port (default: 5432)
    DB_NAME             Database name (default: astro)
    DB_USER             Database user (default: astro_user)
    DB_PASSWORD         Database password
    POSTGRES_USER       PostgreSQL admin user (default: postgres)
    BACKUP_DIR          Backup directory (default: /var/backups/astro-db)
    BACKUP_S3_BUCKET    S3 bucket for backups (for --download-s3 and --list-s3)
    QDRANT_HOST         Qdrant host (default: localhost)
    QDRANT_PORT         Qdrant port (default: 6333)
    QDRANT_COLLECTION   Qdrant collection name (default: astrology_knowledge)

Examples:
    # Restore from local backup (PostgreSQL only)
    $0 /var/backups/astro-db/astro_backup_20250116_030000.sql.gz

    # Restore PostgreSQL and Qdrant
    $0 backup.sql.gz --qdrant qdrant_backup_20250116.snapshot

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

    # List PostgreSQL backups
    local pg_backups=$(find "$BACKUP_DIR" -name "astro_backup_*.sql.gz" -type f 2>/dev/null | sort -r)

    echo "PostgreSQL Backups:"
    echo ""
    printf "%-45s %-12s %-20s\n" "FILENAME" "SIZE" "DATE"
    echo "--------------------------------------------------------------------------------"

    if [ -z "$pg_backups" ]; then
        echo "  No PostgreSQL backups found"
    else
        echo "$pg_backups" | head -10 | while read -r backup; do
            local filename=$(basename "$backup")
            local size=$(ls -lh "$backup" | awk '{print $5}')
            local date=$(ls -l --time-style=long-iso "$backup" 2>/dev/null | awk '{print $6" "$7}' || stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$backup")

            printf "%-45s %-12s %-20s\n" "$filename" "$size" "$date"
        done
    fi

    echo ""
    echo "Qdrant Vector Database Backups:"
    echo ""
    printf "%-45s %-12s %-20s\n" "FILENAME" "SIZE" "DATE"
    echo "--------------------------------------------------------------------------------"

    # List Qdrant backups
    local qdrant_backups=$(find "$BACKUP_DIR" -name "qdrant_backup_*.snapshot" -type f 2>/dev/null | sort -r)

    if [ -z "$qdrant_backups" ]; then
        echo "  No Qdrant backups found"
    else
        echo "$qdrant_backups" | head -10 | while read -r backup; do
            local filename=$(basename "$backup")
            local size=$(ls -lh "$backup" | awk '{print $5}')
            local date=$(ls -l --time-style=long-iso "$backup" 2>/dev/null | awk '{print $6" "$7}' || stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$backup")

            printf "%-45s %-12s %-20s\n" "$filename" "$size" "$date"
        done
    fi

    echo ""
    exit 0
}

download_from_s3() {
    local s3_url="$1"

    if [ -z "$BACKUP_S3_BUCKET" ]; then
        error "BACKUP_S3_BUCKET not configured"
        exit 1
    fi

    log "Downloading backup from S3 using BackupS3Service..."

    # Get filename from S3 URL
    local filename=$(basename "$s3_url" .gz).gz

    # Ensure backup directory exists
    mkdir -p "$BACKUP_DIR"

    local local_path="$BACKUP_DIR/$filename"

    # Call Python BackupS3Service for download
    local result
    result=$(cd "${SCRIPT_DIR}/.." && uv run python -c "
import sys
from pathlib import Path
from app.services.backup_s3_service import backup_s3_service

try:
    success = backup_s3_service.download_backup('$s3_url', Path('$local_path'))
    if success:
        print('SUCCESS')
        sys.exit(0)
    else:
        print('FAILED:Download returned False')
        sys.exit(1)
except Exception as e:
    print(f'ERROR:{e}')
    sys.exit(1)
" 2>&1)

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log "Downloaded successfully: $local_path ✓"
        echo "$local_path"
        return 0
    else
        error "S3 download failed: $result"
        exit 1
    fi
}

list_s3_backups() {
    if [ -z "$BACKUP_S3_BUCKET" ]; then
        error "BACKUP_S3_BUCKET not configured"
        exit 1
    fi

    log "Listing backups from S3..."

    # Call Python BackupS3Service to list backups
    cd "${SCRIPT_DIR}/.." && uv run python -c "
from app.services.backup_s3_service import backup_s3_service

backups = backup_s3_service.list_backups(30)

if not backups:
    print('No backups found in S3')
    exit(0)

print(f'Found {len(backups)} backups in S3:\\n')
print(f'{'Date':<12} {'Size':<10} {'Filename':<40} {'S3 URL':<50}')
print('-' * 115)

for backup in backups:
    size_mb = backup['size'] / (1024 * 1024)
    print(f\"{backup['date']:<12} {size_mb:>8.2f}MB {backup['filename']:<40} {backup['url']:<50}\")
"
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

restore_qdrant() {
    local qdrant_backup_file="$1"

    log "Starting Qdrant vector database restore..."

    local qdrant_url="http://${QDRANT_HOST}:${QDRANT_PORT}"

    # Check if Qdrant is reachable
    if ! curl -sf "${qdrant_url}/healthz" >/dev/null 2>&1; then
        error "Qdrant not reachable at ${qdrant_url}"
        return 1
    fi

    # Check if backup file exists
    if [ ! -f "$qdrant_backup_file" ]; then
        error "Qdrant backup file not found: $qdrant_backup_file"
        return 1
    fi

    local file_size=$(stat -c%s "$qdrant_backup_file" 2>/dev/null || stat -f%z "$qdrant_backup_file" 2>/dev/null)
    log "Qdrant backup file size: $(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B)"

    # Delete existing collection if exists
    log "Deleting existing Qdrant collection '${QDRANT_COLLECTION}'..."
    curl -sf -X DELETE "${qdrant_url}/collections/${QDRANT_COLLECTION}" >/dev/null 2>&1 || true

    # Upload snapshot and restore
    log "Uploading and restoring Qdrant snapshot..."
    log "This may take several minutes depending on snapshot size..."

    local restore_response
    restore_response=$(curl -sf -X POST \
        "${qdrant_url}/collections/${QDRANT_COLLECTION}/snapshots/upload?priority=snapshot" \
        -H "Content-Type: multipart/form-data" \
        -F "snapshot=@${qdrant_backup_file}" 2>&1)

    if [ -z "$restore_response" ]; then
        error "Failed to restore Qdrant snapshot"
        return 1
    fi

    # Check if restore was successful by querying the collection
    sleep 2  # Give Qdrant time to index
    local collection_info
    collection_info=$(curl -sf "${qdrant_url}/collections/${QDRANT_COLLECTION}" 2>/dev/null)

    if [ -z "$collection_info" ]; then
        error "Failed to verify Qdrant restore - collection not found"
        return 1
    fi

    local points_count
    points_count=$(echo "$collection_info" | grep -o '"points_count":[0-9]*' | cut -d: -f2)

    log "Qdrant restore completed: ${points_count:-0} vectors restored ✓"
    return 0
}

verify_qdrant_restore() {
    log "Verifying Qdrant restore..."

    local qdrant_url="http://${QDRANT_HOST}:${QDRANT_PORT}"

    # Check if collection exists and has data
    local collection_info
    collection_info=$(curl -sf "${qdrant_url}/collections/${QDRANT_COLLECTION}" 2>/dev/null)

    if [ -z "$collection_info" ]; then
        error "Qdrant collection '${QDRANT_COLLECTION}' not found after restore"
        return 1
    fi

    local status
    status=$(echo "$collection_info" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

    local points_count
    points_count=$(echo "$collection_info" | grep -o '"points_count":[0-9]*' | cut -d: -f2)

    log "Qdrant collection status: $status"
    log "Qdrant vectors count: ${points_count:-0}"

    if [ "$status" = "green" ]; then
        log "Qdrant verification completed ✓"
        return 0
    else
        log "Qdrant status is '$status' (may still be indexing)"
        return 0
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    local backup_file=""
    local qdrant_backup_file=""
    local skip_confirm=false
    local skip_qdrant=false

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --help|-h)
                usage
                ;;
            --list-backups)
                list_backups
                ;;
            --list-s3)
                list_s3_backups
                exit 0
                ;;
            --qdrant)
                if [ $# -gt 1 ]; then
                    qdrant_backup_file="$2"
                    shift
                else
                    error "--qdrant requires a snapshot file path"
                    usage
                fi
                ;;
            --skip-qdrant)
                skip_qdrant=true
                ;;
            --download-s3)
                # If S3 URL provided as next argument, use it; otherwise get latest
                if [ $# -gt 1 ] && [[ "$2" == s3://* ]]; then
                    backup_file=$(download_from_s3 "$2")
                    shift
                else
                    # Download latest backup (need to implement get_latest_s3_backup)
                    error "--download-s3 requires an S3 URL. Use --list-s3 to see available backups."
                    exit 1
                fi
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
    log "Starting database restore (PostgreSQL + Qdrant)"
    log "=========================================="
    log "PostgreSQL backup: $backup_file"
    log "PostgreSQL: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    if [ -n "$qdrant_backup_file" ]; then
        log "Qdrant backup: $qdrant_backup_file"
    fi
    log "Qdrant: ${QDRANT_HOST}:${QDRANT_PORT} (collection: ${QDRANT_COLLECTION})"

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

    # Perform PostgreSQL restore
    perform_restore "$backup_file"

    # Verify PostgreSQL restore
    verify_restore

    # ==========================================
    # Qdrant Vector Database Restore
    # ==========================================
    if [ "$skip_qdrant" != "true" ]; then
        if [ -n "$qdrant_backup_file" ]; then
            log ""
            log "=========================================="
            log "Starting Qdrant vector database restore"
            log "=========================================="

            if restore_qdrant "$qdrant_backup_file"; then
                verify_qdrant_restore
            else
                log "⚠️  Qdrant restore failed (non-fatal)"
            fi
        else
            # Try to find matching Qdrant backup based on PostgreSQL backup timestamp
            local pg_timestamp=$(basename "$backup_file" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
            if [ -n "$pg_timestamp" ]; then
                local matching_qdrant="$BACKUP_DIR/qdrant_backup_${pg_timestamp}.snapshot"
                if [ -f "$matching_qdrant" ]; then
                    log ""
                    log "=========================================="
                    log "Found matching Qdrant backup, restoring..."
                    log "=========================================="
                    if restore_qdrant "$matching_qdrant"; then
                        verify_qdrant_restore
                    else
                        log "⚠️  Qdrant restore failed (non-fatal)"
                    fi
                else
                    log ""
                    log "No matching Qdrant backup found (use --qdrant to specify one)"
                fi
            fi
        fi
    else
        log ""
        log "Skipping Qdrant restore (--skip-qdrant flag)"
    fi

    # Start application
    start_application

    # Summary
    log ""
    log "=========================================="
    log "All restores completed"
    log "=========================================="
    log "PostgreSQL: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log "Restored from: $backup_file"
    if [ -n "$qdrant_backup_file" ]; then
        log "Qdrant restored from: $qdrant_backup_file"
    fi
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
