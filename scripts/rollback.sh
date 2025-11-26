#!/bin/bash

# rollback.sh - Manual rollback script for Real Astrology application
# Use this script to manually revert to a previous version in case of issues

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to print section headers
print_header() {
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}$1${NC}"
    echo -e "${RED}========================================${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

print_header "🚨 EMERGENCY ROLLBACK - Real Astrology"
log_warning "This script will revert your application to a previous version"
echo ""

# Show current status
log_info "Current commit: $(git rev-parse --short HEAD) - $(git log -1 --pretty=format:'%s')"
log_info "Current branch: $(git branch --show-current)"
echo ""

# Show recent commits
log_info "Recent commits (last 10):"
echo ""
git log --oneline -10 --decorate --color=always
echo ""

# Ask for confirmation
log_warning "⚠️  WARNING: This will stop services and change application version"
echo -n "Do you want to continue with rollback? (yes/no): "
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log_info "Rollback cancelled"
    exit 0
fi

echo ""

# Ask which commit to rollback to
echo -n "Enter the commit hash to rollback to (or press Enter for previous commit): "
read -r COMMIT_HASH

if [ -z "$COMMIT_HASH" ]; then
    # Use previous commit (HEAD~1)
    COMMIT_HASH="HEAD~1"
    log_info "Rolling back to previous commit (HEAD~1)"
else
    log_info "Rolling back to commit: $COMMIT_HASH"
fi

# Validate commit exists
if ! git rev-parse "$COMMIT_HASH" > /dev/null 2>&1; then
    log_error "Invalid commit hash: $COMMIT_HASH"
    exit 1
fi

echo ""
TARGET_COMMIT=$(git rev-parse --short "$COMMIT_HASH")
TARGET_MESSAGE=$(git log -1 --pretty=format:'%s' "$COMMIT_HASH")
log_info "Target commit: $TARGET_COMMIT - $TARGET_MESSAGE"
echo ""

# Final confirmation
log_warning "⚠️  FINAL CONFIRMATION"
log_warning "This will:"
log_warning "  1. Stop all services"
log_warning "  2. Checkout commit $TARGET_COMMIT"
log_warning "  3. Rebuild Docker images"
log_warning "  4. Restart services"
echo ""
echo -n "Are you absolutely sure? Type 'ROLLBACK' to continue: "
read -r FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "ROLLBACK" ]; then
    log_info "Rollback cancelled"
    exit 0
fi

# Start rollback process
print_header "🔄 Starting Rollback Process"

# 1. Stop services
log_info "Stopping services..."
docker compose -f "$COMPOSE_FILE" down
log_success "Services stopped"

# 2. Checkout target commit
log_info "Checking out commit $TARGET_COMMIT..."
git checkout "$COMMIT_HASH"
log_success "Code reverted to $TARGET_COMMIT"

# 3. Rebuild images
log_info "Rebuilding Docker images..."
docker compose -f "$COMPOSE_FILE" build --no-cache api web
log_success "Images rebuilt"

# 4. Start services
log_info "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d
log_success "Services started"

# 5. Wait for services
log_info "Waiting for services to start (15 seconds)..."
sleep 15

# 6. Health check
log_info "Performing health check..."
if curl -f -s http://localhost/health > /dev/null 2>&1; then
    print_header "✅ ROLLBACK SUCCESSFUL"
    log_success "Application is running with commit $TARGET_COMMIT"
    log_info "Services status:"
    docker compose -f "$COMPOSE_FILE" ps
    echo ""
    log_warning "⚠️  Note: You are now in detached HEAD state"
    log_warning "To stay on this version permanently, create a branch:"
    log_info "  git checkout -b rollback-$(date +%Y%m%d-%H%M%S)"
    echo ""
else
    log_error "Health check failed!"
    log_error "Services may not be responding correctly"
    log_info "Check logs with: docker compose -f $COMPOSE_FILE logs"
    echo ""

    echo -n "Do you want to return to main branch? (yes/no): "
    read -r RETURN_CONFIRM

    if [ "$RETURN_CONFIRM" = "yes" ]; then
        log_info "Returning to main branch..."
        docker compose -f "$COMPOSE_FILE" down
        git checkout main
        docker compose -f "$COMPOSE_FILE" up -d
        log_info "Returned to main branch"
    fi

    exit 1
fi
