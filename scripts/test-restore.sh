#!/bin/bash
# Automated Restore Test Script for Astro Application
# Tests the full backup and restore cycle in an isolated environment
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

# Test database configuration
TEST_DB_NAME="${TEST_DB_NAME:-astro_restore_test}"
TEST_DB_USER="${TEST_DB_USER:-astro_user}"
TEST_DB_PASSWORD="${TEST_DB_PASSWORD:-}"
TEST_DB_HOST="${TEST_DB_HOST:-localhost}"
TEST_DB_PORT="${TEST_DB_PORT:-5432}"

# Test backup directory
TEST_BACKUP_DIR="/tmp/astro-restore-test"

# Timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Test backup file
TEST_BACKUP_FILE="$TEST_BACKUP_DIR/test_backup_${TIMESTAMP}.sql.gz"

# Log file
LOG_FILE="/tmp/astro-restore-test-${TIMESTAMP}.log"

# Test user data
TEST_USER_EMAIL="test-restore-${TIMESTAMP}@example.com"
TEST_USER_NAME="Test Restore User"

# Qdrant configuration
QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_TEST_COLLECTION="test_restore_collection"
QDRANT_SNAPSHOT_DIR="/tmp/qdrant-restore-test"
QDRANT_TEST_FAILED=false

# ============================================================================
# Colors for output
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*${NC}" | tee -a "$LOG_FILE" >&2
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $*${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*${NC}" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $*${NC}" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check for required commands
    local missing_commands=()

    # Check PostgreSQL tools
    for cmd in pg_dump pg_restore psql createdb dropdb; do
        if ! command -v $cmd >/dev/null 2>&1; then
            missing_commands+=("$cmd")
        fi
    done

    if [ ${#missing_commands[@]} -gt 0 ]; then
        error "Missing required commands: ${missing_commands[*]}"
        error "Please install PostgreSQL client tools"
        return 1
    fi

    # Check tools for Qdrant testing (curl for API, jq for JSON parsing)
    for cmd in curl jq; do
        if ! command -v $cmd >/dev/null 2>&1; then
            missing_commands+=("$cmd")
        fi
    done

    if [ ${#missing_commands[@]} -gt 0 ]; then
        error "Missing required commands: ${missing_commands[*]}"
        error "Please install curl and jq for Qdrant testing"
        return 1
    fi

    success "Prerequisites check passed"
    return 0
}

create_test_database() {
    log "Creating test database: $TEST_DB_NAME"

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Drop test database if it exists
    dropdb -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" --if-exists "$TEST_DB_NAME" 2>/dev/null || true

    # Create test database
    if createdb -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" "$TEST_DB_NAME"; then
        success "Test database created"
    else
        error "Failed to create test database"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

setup_test_schema() {
    log "Setting up test schema..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Create a simple test table
    psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" <<-EOSQL
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS birth_charts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            person_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
EOSQL

    if [ $? -eq 0 ]; then
        success "Test schema created"
    else
        error "Failed to create test schema"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

insert_test_data() {
    log "Inserting test data..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Insert test user
    psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" <<-EOSQL
        INSERT INTO users (email, full_name) VALUES
            ('$TEST_USER_EMAIL', '$TEST_USER_NAME'),
            ('user2@example.com', 'User Two'),
            ('user3@example.com', 'User Three');

        INSERT INTO birth_charts (user_id, person_name) VALUES
            (1, 'Chart One'),
            (1, 'Chart Two'),
            (2, 'Chart Three');
EOSQL

    if [ $? -eq 0 ]; then
        success "Test data inserted"
    else
        error "Failed to insert test data"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

create_test_backup() {
    log "Creating test backup..."

    mkdir -p "$TEST_BACKUP_DIR"

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    if pg_dump \
        -h "$TEST_DB_HOST" \
        -p "$TEST_DB_PORT" \
        -U "$TEST_DB_USER" \
        -d "$TEST_DB_NAME" \
        --format=custom \
        --compress=9 \
        --file="$TEST_BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
        success "Test backup created: $TEST_BACKUP_FILE"
    else
        error "Failed to create test backup"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD

    # Verify backup file
    if [ ! -f "$TEST_BACKUP_FILE" ]; then
        error "Backup file not found: $TEST_BACKUP_FILE"
        return 1
    fi

    local file_size=$(stat -c%s "$TEST_BACKUP_FILE" 2>/dev/null || stat -f%z "$TEST_BACKUP_FILE" 2>/dev/null)
    info "Backup file size: $(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B)"

    return 0
}

modify_test_data() {
    log "Modifying test data to simulate data changes..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Delete one user and update another
    psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" <<-EOSQL
        DELETE FROM users WHERE email = 'user2@example.com';
        UPDATE users SET full_name = 'Modified User' WHERE email = 'user3@example.com';
        INSERT INTO users (email, full_name) VALUES ('new_user@example.com', 'New User');
EOSQL

    if [ $? -eq 0 ]; then
        success "Test data modified"
    else
        error "Failed to modify test data"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

restore_test_backup() {
    log "Restoring test backup..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Terminate connections
    psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d postgres \
        -v dbname="$TEST_DB_NAME" <<-EOSQL 2>&1 | tee -a "$LOG_FILE" || true
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = :'dbname' AND pid <> pg_backend_pid();
EOSQL

    # Restore backup
    if pg_restore \
        -h "$TEST_DB_HOST" \
        -p "$TEST_DB_PORT" \
        -U "$TEST_DB_USER" \
        -d "$TEST_DB_NAME" \
        --clean \
        --if-exists \
        --no-owner \
        --no-acl \
        "$TEST_BACKUP_FILE" 2>&1 | tee -a "$LOG_FILE"; then
        success "Test backup restored"
    else
        error "Failed to restore test backup"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    return 0
}

validate_restored_data() {
    log "Validating restored data..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Check if test user exists
    local user_exists
    user_exists=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM users WHERE email = '$TEST_USER_EMAIL'" 2>/dev/null | tr -d ' ')

    if [ "$user_exists" != "1" ]; then
        error "Test user not found after restore (expected 1, got $user_exists)"
        unset PGPASSWORD
        return 1
    fi

    # Check user count (should be 3, not 4)
    local user_count
    user_count=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM users" 2>/dev/null | tr -d ' ')

    if [ "$user_count" != "3" ]; then
        error "User count mismatch after restore (expected 3, got $user_count)"
        unset PGPASSWORD
        return 1
    fi

    # Check if user2 is back (should be restored)
    local user2_exists
    user2_exists=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM users WHERE email = 'user2@example.com'" 2>/dev/null | tr -d ' ')

    if [ "$user2_exists" != "1" ]; then
        error "user2 not found after restore (deleted user should be restored)"
        unset PGPASSWORD
        return 1
    fi

    # Check if user3 full_name is reverted
    local user3_name
    user3_name=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT full_name FROM users WHERE email = 'user3@example.com'" 2>/dev/null | tr -d ' ')

    if [ "$user3_name" != "UserThree" ]; then
        error "user3 name not restored (expected 'UserThree', got '$user3_name')"
        unset PGPASSWORD
        return 1
    fi

    # Check if new_user is gone (should not be in backup)
    local new_user_exists
    new_user_exists=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM users WHERE email = 'new_user@example.com'" 2>/dev/null | tr -d ' ')

    if [ "$new_user_exists" != "0" ]; then
        error "new_user found after restore (should not exist in backup)"
        unset PGPASSWORD
        return 1
    fi

    # Check chart count
    local chart_count
    chart_count=$(psql -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM birth_charts" 2>/dev/null | tr -d ' ')

    if [ "$chart_count" != "3" ]; then
        error "Chart count mismatch after restore (expected 3, got $chart_count)"
        unset PGPASSWORD
        return 1
    fi

    unset PGPASSWORD
    success "All data validation checks passed ✓"
    return 0
}

cleanup() {
    log "Cleaning up test environment..."

    if [ -n "$TEST_DB_PASSWORD" ]; then
        export PGPASSWORD="$TEST_DB_PASSWORD"
    fi

    # Drop test database
    dropdb -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" -U "$TEST_DB_USER" --if-exists "$TEST_DB_NAME" 2>/dev/null || true

    unset PGPASSWORD

    # Remove test backup directory
    rm -rf "$TEST_BACKUP_DIR"

    success "Test environment cleaned up"
}

# ============================================================================
# Qdrant Test Functions
# ============================================================================

check_qdrant_available() {
    # Returns 0 if Qdrant is reachable, 1 otherwise
    curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/healthz" >/dev/null 2>&1
}

create_qdrant_test_collection() {
    log "Creating Qdrant test collection: $QDRANT_TEST_COLLECTION"

    local response
    response=$(curl -sf -X PUT "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}" \
        -H "Content-Type: application/json" \
        -d '{
            "vectors": {
                "size": 4,
                "distance": "Cosine"
            }
        }' 2>&1)

    if [ $? -eq 0 ]; then
        success "Qdrant test collection created"
        return 0
    else
        error "Failed to create Qdrant test collection: $response"
        return 1
    fi
}

insert_qdrant_test_vectors() {
    log "Inserting test vectors into Qdrant..."

    local response
    response=$(curl -sf -X PUT "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points" \
        -H "Content-Type: application/json" \
        -d '{
            "points": [
                {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "payload": {"name": "vector1"}},
                {"id": 2, "vector": [0.5, 0.6, 0.7, 0.8], "payload": {"name": "vector2"}},
                {"id": 3, "vector": [0.9, 1.0, 1.1, 1.2], "payload": {"name": "vector3"}}
            ]
        }' 2>&1)

    if [ $? -eq 0 ]; then
        success "Test vectors inserted (3 vectors)"
        return 0
    else
        error "Failed to insert test vectors: $response"
        return 1
    fi
}

create_qdrant_snapshot() {
    log "Creating Qdrant snapshot..."

    local response
    response=$(curl -sf -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/snapshots" 2>&1)

    if [ $? -eq 0 ]; then
        local snapshot_name
        snapshot_name=$(echo "$response" | jq -r '.result.name')
        if [ -n "$snapshot_name" ] && [ "$snapshot_name" != "null" ]; then
            success "Qdrant snapshot created: $snapshot_name"
            echo "$snapshot_name"
            return 0
        fi
    fi

    error "Failed to create Qdrant snapshot: $response"
    return 1
}

download_qdrant_snapshot() {
    local snapshot_name="$1"
    local output_path="$2"

    log "Downloading Qdrant snapshot to: $output_path"

    if curl -sf -o "$output_path" \
        "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/snapshots/${snapshot_name}"; then
        local file_size
        file_size=$(stat -c%s "$output_path" 2>/dev/null || stat -f%z "$output_path" 2>/dev/null)
        success "Snapshot downloaded ($(numfmt --to=iec-i --suffix=B $file_size 2>/dev/null || echo ${file_size}B))"
        return 0
    else
        error "Failed to download Qdrant snapshot"
        return 1
    fi
}

modify_qdrant_data() {
    log "Modifying Qdrant data to simulate changes..."

    # Delete vector 2
    local delete_response
    delete_response=$(curl -sf -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points/delete" \
        -H "Content-Type: application/json" \
        -d '{"points": [2]}' 2>&1)

    if [ $? -ne 0 ]; then
        error "Failed to delete vector 2: $delete_response"
        return 1
    fi

    # Add vector 4 (post-backup)
    local insert_response
    insert_response=$(curl -sf -X PUT "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points" \
        -H "Content-Type: application/json" \
        -d '{
            "points": [
                {"id": 4, "vector": [1.3, 1.4, 1.5, 1.6], "payload": {"name": "vector4_post_backup"}}
            ]
        }' 2>&1)

    if [ $? -eq 0 ]; then
        success "Qdrant data modified (deleted vector 2, added vector 4)"
        return 0
    else
        error "Failed to add vector 4: $insert_response"
        return 1
    fi
}

restore_qdrant_snapshot() {
    local snapshot_path="$1"

    log "Restoring Qdrant from snapshot..."

    # Delete current collection
    curl -sf -X DELETE "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}" >/dev/null 2>&1 || true

    # Wait a moment for deletion to complete
    sleep 1

    # Restore from snapshot using upload endpoint
    local response
    response=$(curl -sf -X POST "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/snapshots/upload?priority=snapshot" \
        -H "Content-Type: multipart/form-data" \
        -F "snapshot=@${snapshot_path}" 2>&1)

    if [ $? -eq 0 ]; then
        success "Qdrant snapshot restored"
        # Wait for restore to complete
        sleep 2
        return 0
    else
        error "Failed to restore Qdrant snapshot: $response"
        return 1
    fi
}

validate_qdrant_restore() {
    log "Validating Qdrant restored data..."

    local errors=0

    # Check vector count (should be 3, not 2 or 4)
    local count_response
    count_response=$(curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}" 2>&1)
    local count
    count=$(echo "$count_response" | jq -r '.result.points_count')

    if [ "$count" != "3" ]; then
        error "Qdrant: Expected 3 vectors, got $count"
        ((errors++))
    else
        info "Vector count: $count (expected 3) ✓"
    fi

    # Check vector 2 exists (was deleted post-backup, should be restored)
    local v2_response
    v2_response=$(curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points/2" 2>&1)
    local v2_exists
    v2_exists=$(echo "$v2_response" | jq -r '.result | length')

    if [ "$v2_exists" == "0" ] || [ "$v2_exists" == "null" ] || [ -z "$v2_exists" ]; then
        error "Qdrant: Vector 2 not restored (deleted user should be restored)"
        ((errors++))
    else
        info "Vector 2 exists (restored) ✓"
    fi

    # Check vector 4 does NOT exist (added post-backup, should not be in restore)
    local v4_status
    v4_status=$(curl -sf -o /dev/null -w "%{http_code}" "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points/4" 2>&1)

    # A 404 or empty result means vector doesn't exist (expected)
    local v4_response
    v4_response=$(curl -sf "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}/points/4" 2>&1)
    local v4_result
    v4_result=$(echo "$v4_response" | jq -r '.result | length' 2>/dev/null)

    if [ "$v4_result" != "0" ] && [ "$v4_result" != "null" ] && [ -n "$v4_result" ]; then
        error "Qdrant: Vector 4 should not exist (added post-backup)"
        ((errors++))
    else
        info "Vector 4 does not exist (correct) ✓"
    fi

    if [ $errors -eq 0 ]; then
        success "All Qdrant validation checks passed ✓"
        return 0
    else
        error "Qdrant validation failed with $errors error(s)"
        return 1
    fi
}

cleanup_qdrant() {
    log "Cleaning up Qdrant test environment..."

    # Delete test collection
    curl -sf -X DELETE "http://${QDRANT_HOST}:${QDRANT_PORT}/collections/${QDRANT_TEST_COLLECTION}" >/dev/null 2>&1 || true

    # Remove snapshot directory
    rm -rf "$QDRANT_SNAPSHOT_DIR" 2>/dev/null || true

    success "Qdrant test environment cleaned up"
}

# ============================================================================
# Main Test Process
# ============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "  Database Restore Test"
    echo "=========================================="
    echo "Test database: $TEST_DB_NAME"
    echo "Test backup: $TEST_BACKUP_FILE"
    echo "Log file: $LOG_FILE"
    echo "=========================================="
    echo ""

    local failed=false

    # Check prerequisites
    if ! check_prerequisites; then
        error "Prerequisites check failed"
        exit 1
    fi

    # Step 1: Create test database
    info "Step 1/7: Creating test database..."
    if ! create_test_database; then
        error "Step 1 failed"
        cleanup
        exit 1
    fi

    # Step 2: Setup schema
    info "Step 2/7: Setting up test schema..."
    if ! setup_test_schema; then
        error "Step 2 failed"
        cleanup
        exit 1
    fi

    # Step 3: Insert test data
    info "Step 3/7: Inserting test data..."
    if ! insert_test_data; then
        error "Step 3 failed"
        cleanup
        exit 1
    fi

    # Step 4: Create backup
    info "Step 4/7: Creating test backup..."
    if ! create_test_backup; then
        error "Step 4 failed"
        cleanup
        exit 1
    fi

    # Step 5: Modify data
    info "Step 5/7: Modifying test data..."
    if ! modify_test_data; then
        error "Step 5 failed"
        cleanup
        exit 1
    fi

    # Step 6: Restore backup
    info "Step 6/7: Restoring test backup..."
    if ! restore_test_backup; then
        error "Step 6 failed"
        cleanup
        exit 1
    fi

    # Step 7: Validate restored data
    info "Step 7/7: Validating restored data..."
    if ! validate_restored_data; then
        error "Step 7 failed"
        failed=true
    fi

    # Cleanup PostgreSQL
    cleanup

    # ========================================
    # Qdrant Backup/Restore Test
    # ========================================
    echo ""
    echo "=========================================="
    echo "  Qdrant Backup/Restore Test"
    echo "=========================================="

    if check_qdrant_available; then
        info "Qdrant available at ${QDRANT_HOST}:${QDRANT_PORT}"
        mkdir -p "$QDRANT_SNAPSHOT_DIR"

        local SNAPSHOT_NAME=""

        # Step 1: Create test collection
        info "[Qdrant Step 1/6] Creating test collection..."
        if ! create_qdrant_test_collection; then
            error "Qdrant Step 1 failed"
            QDRANT_TEST_FAILED=true
        fi

        # Step 2: Insert test vectors
        if [ "$QDRANT_TEST_FAILED" != "true" ]; then
            info "[Qdrant Step 2/6] Inserting test vectors..."
            if ! insert_qdrant_test_vectors; then
                error "Qdrant Step 2 failed"
                QDRANT_TEST_FAILED=true
            fi
        fi

        # Step 3: Create snapshot
        if [ "$QDRANT_TEST_FAILED" != "true" ]; then
            info "[Qdrant Step 3/6] Creating snapshot..."
            SNAPSHOT_NAME=$(create_qdrant_snapshot)
            if [ -z "$SNAPSHOT_NAME" ] || [ "$SNAPSHOT_NAME" == "null" ]; then
                error "Qdrant Step 3 failed"
                QDRANT_TEST_FAILED=true
            else
                # Download snapshot
                if ! download_qdrant_snapshot "$SNAPSHOT_NAME" "$QDRANT_SNAPSHOT_DIR/test.snapshot"; then
                    error "Qdrant Step 3 failed (download)"
                    QDRANT_TEST_FAILED=true
                fi
            fi
        fi

        # Step 4: Modify data
        if [ "$QDRANT_TEST_FAILED" != "true" ]; then
            info "[Qdrant Step 4/6] Modifying data (simulating changes)..."
            if ! modify_qdrant_data; then
                error "Qdrant Step 4 failed"
                QDRANT_TEST_FAILED=true
            fi
        fi

        # Step 5: Restore from snapshot
        if [ "$QDRANT_TEST_FAILED" != "true" ]; then
            info "[Qdrant Step 5/6] Restoring from snapshot..."
            if ! restore_qdrant_snapshot "$QDRANT_SNAPSHOT_DIR/test.snapshot"; then
                error "Qdrant Step 5 failed"
                QDRANT_TEST_FAILED=true
            fi
        fi

        # Step 6: Validate restored data
        if [ "$QDRANT_TEST_FAILED" != "true" ]; then
            info "[Qdrant Step 6/6] Validating restored data..."
            if ! validate_qdrant_restore; then
                error "Qdrant Step 6 failed"
                QDRANT_TEST_FAILED=true
            fi
        fi

        # Cleanup Qdrant
        cleanup_qdrant
    else
        warn "Qdrant not available at ${QDRANT_HOST}:${QDRANT_PORT}, skipping Qdrant tests"
    fi

    # Summary
    echo ""
    echo "=========================================="
    if [ "$failed" = true ] || [ "$QDRANT_TEST_FAILED" = true ]; then
        error "RESTORE TEST FAILED"
        echo "=========================================="
        echo "See log file for details: $LOG_FILE"
        echo ""
        echo "Summary:"
        if [ "$failed" = true ]; then
            echo "  - PostgreSQL restore: FAILED ✗"
        else
            echo "  - PostgreSQL restore: PASSED ✓"
        fi
        if [ "$QDRANT_TEST_FAILED" = true ]; then
            echo "  - Qdrant restore: FAILED ✗"
        elif check_qdrant_available; then
            echo "  - Qdrant restore: PASSED ✓"
        else
            echo "  - Qdrant restore: SKIPPED (not available)"
        fi
        echo ""
        exit 1
    else
        success "RESTORE TEST PASSED ✓"
        echo "=========================================="
        echo "All tests completed successfully!"
        echo "Log file: $LOG_FILE"
        echo ""
        echo "Summary - PostgreSQL:"
        echo "  - Test database created ✓"
        echo "  - Test data inserted ✓"
        echo "  - Backup created ✓"
        echo "  - Data modified ✓"
        echo "  - Backup restored ✓"
        echo "  - Data validation passed ✓"
        echo "  - Cleanup completed ✓"
        echo ""
        if check_qdrant_available; then
            echo "Summary - Qdrant:"
            echo "  - Test collection created ✓"
            echo "  - Test vectors inserted ✓"
            echo "  - Snapshot created ✓"
            echo "  - Data modified ✓"
            echo "  - Snapshot restored ✓"
            echo "  - Data validation passed ✓"
            echo "  - Cleanup completed ✓"
            echo ""
        else
            echo "Qdrant: Skipped (not available)"
            echo ""
        fi
        exit 0
    fi
}

# ============================================================================
# Execute
# ============================================================================

# Create log file parent directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main

exit $?
