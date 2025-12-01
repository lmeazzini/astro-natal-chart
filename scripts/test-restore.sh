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

    # Cleanup
    cleanup

    # Summary
    echo ""
    echo "=========================================="
    if [ "$failed" = true ]; then
        error "RESTORE TEST FAILED"
        echo "=========================================="
        echo "See log file for details: $LOG_FILE"
        exit 1
    else
        success "RESTORE TEST PASSED ✓"
        echo "=========================================="
        echo "All tests completed successfully!"
        echo "Log file: $LOG_FILE"
        echo ""
        echo "Summary:"
        echo "  - Test database created ✓"
        echo "  - Test data inserted ✓"
        echo "  - Backup created ✓"
        echo "  - Data modified ✓"
        echo "  - Backup restored ✓"
        echo "  - Data validation passed ✓"
        echo "  - Cleanup completed ✓"
        echo ""
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
