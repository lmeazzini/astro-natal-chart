#!/bin/bash

# deploy.sh - Production deployment script for Real Astrology application
# This script handles automatic deployment with health checks and rollback capability

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
HEALTH_CHECK_URL="http://localhost/health"
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=2
MIN_DISK_SPACE_GB=5

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
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

print_header "🚀 REAL ASTROLOGY - PRODUCTION DEPLOYMENT"
log_info "Starting deployment process..."
echo ""

# ============================================
# 1. Pre-deployment validations
# ============================================
check_prerequisites() {
    print_header "1️⃣  Pre-deployment Checks"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running!"
        exit 1
    fi
    log_success "Docker is running"

    # Check if docker-compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    log_success "Docker Compose file found"

    # Check if .env files exist
    if [ ! -f "apps/api/.env" ]; then
        log_error "Backend .env file not found: apps/api/.env"
        exit 1
    fi
    log_success "Environment files found"

    # Check disk space (need at least 5GB free)
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt "$MIN_DISK_SPACE_GB" ]; then
        log_error "Not enough disk space! Available: ${AVAILABLE_SPACE}GB, Required: ${MIN_DISK_SPACE_GB}GB"
        exit 1
    fi
    log_success "Sufficient disk space available: ${AVAILABLE_SPACE}GB"

    log_success "All pre-deployment checks passed"
}

# ============================================
# 2. Tag current images for rollback
# ============================================
tag_current_images() {
    print_header "2️⃣  Creating Rollback Point"

    # Tag current API image
    if docker image inspect astro-api-prod:latest > /dev/null 2>&1; then
        docker tag astro-api-prod:latest astro-api-prod:rollback || true
        log_success "Tagged current API image for rollback"
    else
        log_warning "No existing API image to tag (first deployment?)"
    fi

    # Tag current Web image
    if docker image inspect astro-web-prod:latest > /dev/null 2>&1; then
        docker tag astro-web-prod:latest astro-web-prod:rollback || true
        log_success "Tagged current Web image for rollback"
    else
        log_warning "No existing Web image to tag (first deployment?)"
    fi
}

# ============================================
# 3. Pull latest code and build images
# ============================================
build_images() {
    print_header "3️⃣  Building New Images"

    # Pull latest code
    log_info "Pulling latest code from main branch..."
    git fetch origin main
    git reset --hard origin/main
    log_success "Code updated to latest version"

    # Show current commit
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s")
    log_info "Deploying commit: $CURRENT_COMMIT - $COMMIT_MESSAGE"

    # Build new images
    log_info "Building Docker images (this may take a few minutes)..."
    docker compose -f "$COMPOSE_FILE" build --no-cache api web
    log_success "Images built successfully"
}

# ============================================
# 4. Run database migrations
# ============================================
run_migrations() {
    print_header "4️⃣  Running Database Migrations"

    # Check for recent backup
    if [ -d "backups" ]; then
        LAST_BACKUP=$(find backups/ -name "*.sql.gz" -mtime -1 2>/dev/null | wc -l)
        if [ "$LAST_BACKUP" -eq 0 ]; then
            log_warning "⚠️  No recent backup found (>24 hours old)"
            log_warning "It's recommended to have a recent backup before migrations"
            log_info "Continuing in 5 seconds... (Press Ctrl+C to cancel)"
            sleep 5
        else
            log_success "Recent backup found"
        fi
    else
        log_warning "Backup directory not found"
    fi

    # Check current and target migration versions
    log_info "Checking migration status..."

    # Ensure database is running
    docker compose -f "$COMPOSE_FILE" up -d db
    sleep 3

    # Run migrations
    log_info "Applying database migrations..."
    docker compose -f "$COMPOSE_FILE" run --rm api uv run alembic upgrade head

    log_success "Database migrations completed"
}

# ============================================
# 5. Restart services with minimal downtime
# ============================================
restart_services() {
    print_header "5️⃣  Restarting Services"

    log_info "Starting/restarting application services..."

    # Start all services
    docker compose -f "$COMPOSE_FILE" up -d

    log_info "Waiting for services to start (10 seconds)..."
    sleep 10

    # Reload Nginx to pick up any config changes
    log_info "Reloading Nginx configuration..."
    docker compose -f "$COMPOSE_FILE" exec -T nginx nginx -s reload || log_warning "Nginx reload failed (may not be running yet)"

    log_success "Services restarted"
}

# ============================================
# 6. Health check with auto-rollback
# ============================================
health_check() {
    print_header "6️⃣  Health Check & Validation"

    log_info "Performing health checks..."

    for i in $(seq 1 $HEALTH_CHECK_RETRIES); do
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log_success "✅ Health check passed!"
            log_success "Application is responding correctly"
            return 0
        fi

        if [ $i -eq $HEALTH_CHECK_RETRIES ]; then
            log_error "❌ Health check failed after $HEALTH_CHECK_RETRIES attempts"
            return 1
        fi

        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
    done
}

# ============================================
# 7. Automatic rollback on failure
# ============================================
rollback() {
    print_header "🔄 ROLLBACK - Reverting to Previous Version"

    log_warning "Rolling back to previous version..."

    # Restore rollback tags
    if docker image inspect astro-api-prod:rollback > /dev/null 2>&1; then
        docker tag astro-api-prod:rollback astro-api-prod:latest
        log_info "Restored API image"
    fi

    if docker image inspect astro-web-prod:rollback > /dev/null 2>&1; then
        docker tag astro-web-prod:rollback astro-web-prod:latest
        log_info "Restored Web image"
    fi

    # Restart with old images
    docker compose -f "$COMPOSE_FILE" up -d --no-deps api web
    log_warning "Rollback completed - running previous version"

    # Final health check
    sleep 10
    if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        log_success "Application is running with previous version"
    else
        log_error "Health check still failing after rollback!"
        log_error "Manual intervention required!"
    fi
}

# ============================================
# 8. Cleanup old images
# ============================================
cleanup_old_images() {
    print_header "8️⃣  Cleanup"

    log_info "Removing old Docker images..."
    docker image prune -f > /dev/null 2>&1 || true
    log_success "Cleanup completed"
}

# ============================================
# Main execution flow
# ============================================
main() {
    # Run deployment steps
    check_prerequisites
    tag_current_images
    build_images
    run_migrations
    restart_services

    # Validate deployment
    if health_check; then
        cleanup_old_images

        print_header "✅ DEPLOYMENT SUCCESSFUL"
        log_success "Application deployed successfully!"
        log_info "Commit: $(git rev-parse --short HEAD)"
        log_info "Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""

        exit 0
    else
        log_error "Health check failed - initiating rollback..."
        rollback

        print_header "❌ DEPLOYMENT FAILED"
        log_error "Deployment failed and was rolled back"
        log_error "Please check logs for details"
        echo ""

        exit 1
    fi
}

# Run main function
main
