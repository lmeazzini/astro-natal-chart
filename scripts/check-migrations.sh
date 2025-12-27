#!/bin/bash
# Migration verification script for Real Astrology
# Usage: ./scripts/check-migrations.sh
#
# This script checks the health and status of Alembic migrations.
# Run before deploying to production to ensure migrations are in a good state.
#
# The script runs alembic commands inside the Docker container.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to project root directory
cd "$(dirname "$0")/.."

# Function to run alembic commands inside Docker
run_alembic() {
    docker compose exec -T api uv run alembic "$@" 2>/dev/null
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Migration Health Check                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if Docker is running
if ! docker compose ps api --status running | grep -q "api"; then
    echo -e "${RED}✗ API container is not running${NC}"
    echo "  Run 'docker compose up -d' to start the services"
    exit 1
fi

# Check 1: Current migration state
echo -e "${YELLOW}▶ Current Migration State${NC}"
echo "─────────────────────────────────────────────────────────────"
CURRENT=$(run_alembic current || echo "ERROR")
if [[ "$CURRENT" == *"ERROR"* ]] || [[ -z "$CURRENT" ]]; then
    echo -e "${RED}✗ Unable to determine current migration state${NC}"
    echo "  Make sure the database is running and accessible"
    exit 1
else
    echo -e "${GREEN}✓ Current revision:${NC}"
    echo "  $CURRENT"
fi
echo

# Check 2: Migration heads (should be exactly one)
echo -e "${YELLOW}▶ Checking for Multiple Heads${NC}"
echo "─────────────────────────────────────────────────────────────"
HEADS_OUTPUT=$(run_alembic heads)
HEADS=$(echo "$HEADS_OUTPUT" | grep -c "^" || echo "0")
if [[ "$HEADS" -gt 1 ]]; then
    echo -e "${RED}✗ WARNING: Multiple heads detected ($HEADS heads)${NC}"
    echo "  This indicates branching migrations that need to be merged."
    echo "  Run: docker compose exec api uv run alembic merge heads -m 'merge_heads'"
    echo "$HEADS_OUTPUT"
    echo
    ISSUES_FOUND=1
elif [[ "$HEADS" -eq 1 ]]; then
    echo -e "${GREEN}✓ Single head found (good)${NC}"
    echo "  $HEADS_OUTPUT"
else
    echo -e "${RED}✗ No heads found${NC}"
    ISSUES_FOUND=1
fi
echo

# Check 3: Pending migrations
echo -e "${YELLOW}▶ Pending Migrations${NC}"
echo "─────────────────────────────────────────────────────────────"
PENDING_SQL=$(run_alembic upgrade head --sql 2>/dev/null || echo "")
PENDING=$(echo "$PENDING_SQL" | grep -c "^--" || echo "0")
if [[ "$PENDING" -gt 0 ]] && [[ -n "$PENDING_SQL" ]]; then
    echo -e "${YELLOW}⚠ There are pending migrations to apply${NC}"
    echo "  Preview (first 20 SQL statements):"
    echo "$PENDING_SQL" | head -30
else
    echo -e "${GREEN}✓ Database is up to date${NC}"
fi
echo

# Check 4: Recent migration history
echo -e "${YELLOW}▶ Recent Migration History (last 10)${NC}"
echo "─────────────────────────────────────────────────────────────"
run_alembic history -v | head -40
echo

# Check 5: Downgrade safety
echo -e "${YELLOW}▶ Downgrade Safety Check${NC}"
echo "─────────────────────────────────────────────────────────────"
# Count migrations without downgrade (empty downgrade functions)
MIGRATION_DIR="apps/api/alembic/versions"
if [[ -d "$MIGRATION_DIR" ]]; then
    TOTAL_MIGRATIONS=$(find "$MIGRATION_DIR" -name "*.py" -not -name "__pycache__" | wc -l)
    # Check for migrations with empty downgrade (just 'pass')
    EMPTY_DOWNGRADE=$(grep -l "def downgrade.*:" "$MIGRATION_DIR"/*.py 2>/dev/null | xargs grep -l "^[[:space:]]*pass[[:space:]]*$" 2>/dev/null | wc -l || echo "0")

    if [[ "$EMPTY_DOWNGRADE" -gt 0 ]]; then
        echo -e "${YELLOW}⚠ $EMPTY_DOWNGRADE migration(s) may have empty downgrade() functions${NC}"
        echo "  These migrations cannot be rolled back safely."
    else
        echo -e "${GREEN}✓ All $TOTAL_MIGRATIONS migrations checked${NC}"
    fi
else
    echo -e "${RED}✗ Migration directory not found${NC}"
fi
echo

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Summary                                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

if [[ -n "$ISSUES_FOUND" ]]; then
    echo -e "${RED}✗ Issues were found. Please review before deploying.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All checks passed. Migrations are healthy.${NC}"
    exit 0
fi
