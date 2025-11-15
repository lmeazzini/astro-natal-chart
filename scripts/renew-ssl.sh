#!/bin/bash

# renew-ssl.sh - Manually renew SSL certificates
# This script forces a certificate renewal (useful for testing or manual renewal)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

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

print_header "🔄 SSL CERTIFICATE RENEWAL"

# Check if running in dry-run mode
if [ "$1" = "--dry-run" ]; then
    log_warning "Running in DRY-RUN mode (no actual renewal)"
    DRY_RUN="--dry-run"
else
    log_info "Running LIVE renewal"
    DRY_RUN=""
fi

echo ""

# Step 1: Check current certificates
print_header "📜 Step 1: Checking current certificates"
log_info "Listing current certificates..."
docker compose -f docker-compose.prod.yml run --rm certbot certificates
echo ""

# Step 2: Renew certificates
print_header "🔄 Step 2: Renewing certificates"
log_info "Running certbot renew..."

docker compose -f docker-compose.prod.yml run --rm certbot renew $DRY_RUN

if [ $? -eq 0 ]; then
    log_success "Certificate renewal completed"
else
    log_warning "No certificates were renewed (they may not be due for renewal yet)"
    log_info "Certificates are renewed automatically when < 30 days until expiration"
fi
echo ""

# Step 3: Reload nginx
if [ -z "$DRY_RUN" ]; then
    print_header "🔄 Step 3: Reloading nginx"
    log_info "Reloading nginx to apply new certificates..."
    docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

    if [ $? -eq 0 ]; then
        log_success "Nginx reloaded successfully"
    else
        log_warning "Failed to reload nginx. Try: docker compose -f docker-compose.prod.yml restart nginx"
    fi
    echo ""
fi

# Final message
print_header "✅ RENEWAL COMPLETE"

if [ "$DRY_RUN" = "--dry-run" ]; then
    log_info "This was a dry-run. No certificates were actually renewed."
    log_info "To perform a real renewal, run: $0"
else
    log_success "SSL certificates have been renewed (if they were due)"
    log_info "Certificates are automatically renewed by the certbot container every 12 hours"
fi

echo ""
log_info "To check certificate expiration:"
echo "  docker compose -f docker-compose.prod.yml run --rm certbot certificates"
echo ""

exit 0
