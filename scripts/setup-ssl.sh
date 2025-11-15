#!/bin/bash

# setup-ssl.sh - Setup SSL certificates with Let's Encrypt for production
# This script obtains SSL certificates from Let's Encrypt and configures nginx

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

print_header() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Check parameters
if [ $# -lt 2 ]; then
    echo "Usage: $0 <domain> <email> [staging]"
    echo ""
    echo "Arguments:"
    echo "  domain   - Your domain name (e.g., example.com)"
    echo "  email    - Email for Let's Encrypt notifications"
    echo "  staging  - Optional: use 'staging' for testing"
    echo ""
    echo "Examples:"
    echo "  $0 astro.example.com admin@example.com           # Production"
    echo "  $0 astro.example.com admin@example.com staging   # Test/staging"
    exit 1
fi

DOMAIN=$1
EMAIL=$2
STAGING=${3:-}

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

print_header "🔐 SSL CERTIFICATE SETUP - LET'S ENCRYPT"
log_info "Domain: $DOMAIN"
log_info "Email: $EMAIL"

if [ "$STAGING" = "staging" ]; then
    log_warning "Running in STAGING mode (test certificates)"
    STAGING_FLAG="--staging"
else
    log_info "Running in PRODUCTION mode (real certificates)"
    STAGING_FLAG=""
fi

echo ""

# Step 1: Create directories
print_header "📁 Step 1: Creating directories"
mkdir -p certbot/conf certbot/www nginx/logs
log_success "Directories created"
echo ""

# Step 2: Update nginx configuration with actual domain
print_header "🔧 Step 2: Updating nginx configuration"
log_info "Updating domain in nginx/conf.d/astro.conf..."

if [ -f "nginx/conf.d/astro.conf" ]; then
    # Backup original
    cp nginx/conf.d/astro.conf nginx/conf.d/astro.conf.bak

    # Replace server_name and SSL paths
    sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" nginx/conf.d/astro.conf
    sed -i "s|/etc/letsencrypt/live/example.com/|/etc/letsencrypt/live/$DOMAIN/|g" nginx/conf.d/astro.conf

    log_success "Nginx configuration updated"
else
    log_error "nginx/conf.d/astro.conf not found!"
    exit 1
fi
echo ""

# Step 3: Start nginx in HTTP-only mode (for ACME challenge)
print_header "🚀 Step 3: Starting nginx (HTTP only)"
log_info "Starting nginx to serve ACME challenge..."

# Temporarily comment out SSL configuration
cp nginx/conf.d/astro.conf nginx/conf.d/astro.conf.pre-ssl
sed -i '/#.*HTTPS Server/,$ s/^/# /' nginx/conf.d/astro.conf

# Start nginx
docker compose -f docker-compose.prod.yml up -d nginx

sleep 3
log_success "Nginx started"
echo ""

# Step 4: Obtain SSL certificate
print_header "📜 Step 4: Obtaining SSL certificate from Let's Encrypt"
log_info "This may take a minute..."

# Run certbot to obtain certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    $STAGING_FLAG \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

if [ $? -eq 0 ]; then
    log_success "SSL certificate obtained successfully!"
else
    log_error "Failed to obtain SSL certificate"
    log_info "Restoring original nginx configuration..."
    mv nginx/conf.d/astro.conf.pre-ssl nginx/conf.d/astro.conf
    docker compose -f docker-compose.prod.yml restart nginx
    exit 1
fi
echo ""

# Step 5: Enable HTTPS in nginx
print_header "🔓 Step 5: Enabling HTTPS in nginx"
log_info "Restoring full nginx configuration with SSL..."

# Restore original configuration (with updated domain)
mv nginx/conf.d/astro.conf.pre-ssl nginx/conf.d/astro.conf

# Reload nginx to apply SSL configuration
docker compose -f docker-compose.prod.yml restart nginx

sleep 2
log_success "HTTPS enabled"
echo ""

# Step 6: Verify SSL
print_header "✅ Step 6: Verifying SSL certificate"
log_info "Checking certificate validity..."

# Check if certificate exists
if docker compose -f docker-compose.prod.yml exec -T nginx ls /etc/letsencrypt/live/$DOMAIN/fullchain.pem > /dev/null 2>&1; then
    log_success "Certificate files found"

    # Show certificate info
    docker compose -f docker-compose.prod.yml exec -T certbot certbot certificates | grep -A 10 "$DOMAIN"
else
    log_warning "Certificate files not found in expected location"
fi
echo ""

# Step 7: Test renewal
print_header "🔄 Step 7: Testing certificate renewal"
log_info "Running dry-run renewal test..."

docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

if [ $? -eq 0 ]; then
    log_success "Renewal test passed! Auto-renewal is configured."
else
    log_warning "Renewal test failed. Check certbot logs."
fi
echo ""

# Final instructions
print_header "🎉 SSL SETUP COMPLETE"

if [ "$STAGING" = "staging" ]; then
    log_warning "You used STAGING certificates (not trusted by browsers)"
    log_info "To get production certificates, run:"
    echo -e "  ${YELLOW}$0 $DOMAIN $EMAIL${NC}"
else
    log_success "Production SSL certificates installed!"
fi

echo ""
log_info "Your site should now be accessible at:"
echo -e "  ${GREEN}https://$DOMAIN${NC}"
echo -e "  ${GREEN}https://www.$DOMAIN${NC}"
echo ""

log_info "Next steps:"
echo "1. Update .env.production:"
echo "   - Set DOMAIN=$DOMAIN"
echo "   - Set ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN"
echo "   - Set COOKIE_SECURE=true"
echo "   - Set COOKIE_DOMAIN=$DOMAIN"
echo ""
echo "2. Test your site:"
echo "   - https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "   - https://securityheaders.com/?q=$DOMAIN"
echo ""
echo "3. Monitor certificate expiration:"
echo "   - Certificates auto-renew every 12 hours via certbot container"
echo "   - Expires in 90 days, renews when < 30 days remaining"
echo ""

exit 0
