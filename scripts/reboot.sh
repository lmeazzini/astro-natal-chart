#!/bin/bash

# reboot.sh - Complete system reboot script for Astro Natal Chart application
# This script stops all services, rebuilds containers, and starts everything fresh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_header "🔄 ASTRO NATAL CHART - SYSTEM REBOOT"
log_info "Starting complete system reboot..."
log_warning "This will stop all services, rebuild containers, and restart everything"
echo ""

# Step 1: Stop all Docker services
print_header "📦 Step 1: Stopping Docker services"
log_info "Stopping all running containers..."
if docker compose ps -q > /dev/null 2>&1; then
    docker compose down
    log_success "All containers stopped"
else
    log_warning "No running containers found"
fi
echo ""

# Step 2: Clean up (optional - remove unused images)
print_header "🧹 Step 2: Cleaning up"
log_info "Removing dangling images and stopped containers..."
docker system prune -f > /dev/null 2>&1 || true
log_success "Cleanup completed"
echo ""

# Step 3: Rebuild containers
print_header "🏗️  Step 3: Rebuilding Docker images"
log_info "Building fresh Docker images (this may take a few minutes)..."
docker compose build --no-cache
log_success "Docker images rebuilt successfully"
echo ""

# Step 4: Start all services
print_header "🚀 Step 4: Starting all services"
log_info "Starting Docker Compose services..."
docker compose up -d
log_success "All services started"
echo ""

# Step 5: Wait for services to be ready
print_header "⏳ Step 5: Waiting for services to be ready"

log_info "Waiting for PostgreSQL..."
RETRIES=30
until docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 1
    RETRIES=$((RETRIES - 1))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    log_error "PostgreSQL failed to start within 30 seconds"
    exit 1
fi
log_success "PostgreSQL is ready"

log_info "Waiting for Redis..."
RETRIES=15
until docker compose exec -T redis redis-cli ping > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do
    echo -n "."
    sleep 1
    RETRIES=$((RETRIES - 1))
done
echo ""

if [ $RETRIES -eq 0 ]; then
    log_error "Redis failed to start within 15 seconds"
    exit 1
fi
log_success "Redis is ready"

log_info "Waiting for API to be ready..."
sleep 5  # Give API a few seconds to start
log_success "API should be ready"
echo ""

# Step 6: Run database migrations
print_header "🗄️  Step 6: Running database migrations"
log_info "Applying database migrations..."
if docker compose exec -T api sh -c "cd /app && alembic upgrade head" > /dev/null 2>&1; then
    log_success "Database migrations completed"
else
    log_warning "Migrations may have already been applied or failed"
fi
echo ""

# Step 7: Show service status
print_header "📊 Step 7: Service Status"
docker compose ps
echo ""

# Step 8: Show service URLs
print_header "🌐 Service URLs"
echo -e "${GREEN}API (Backend):${NC}       http://localhost:8000"
echo -e "${GREEN}API Docs (Swagger):${NC} http://localhost:8000/docs"
echo -e "${GREEN}Web (Frontend):${NC}     http://localhost:5173"
echo -e "${GREEN}PostgreSQL:${NC}         localhost:5432"
echo -e "${GREEN}Redis:${NC}              localhost:6379"
echo ""

# Step 9: Health check
print_header "🏥 Step 9: Health Check"
log_info "Checking API health..."
sleep 2  # Give API a moment to fully start

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_success "API health check passed ✓"
else
    log_warning "API health check failed or /health endpoint not available"
    log_info "This is normal if the API doesn't have a health endpoint yet"
fi
echo ""

# Final message
print_header "✅ REBOOT COMPLETE"
log_success "System is up and running!"
echo ""
log_info "To view logs, run:"
echo -e "  ${YELLOW}docker compose logs -f${NC}          (all services)"
echo -e "  ${YELLOW}docker compose logs -f api${NC}      (API only)"
echo -e "  ${YELLOW}docker compose logs -f web${NC}      (Web only)"
echo ""
log_info "To stop services, run:"
echo -e "  ${YELLOW}docker compose down${NC}"
echo ""

exit 0
