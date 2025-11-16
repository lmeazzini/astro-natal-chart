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

# Step 0: Pre-flight checks
print_header "🔍 Step 0: Pre-flight checks"

# Check if domain resolves to this server
log_info "Checking DNS resolution for $DOMAIN..."
DOMAIN_IP=$(dig +short "$DOMAIN" | tail -1)
if [ -z "$DOMAIN_IP" ]; then
    log_error "Domain $DOMAIN does not resolve to any IP address"
    log_info "Please configure your DNS before running this script"
    exit 1
else
    log_success "Domain resolves to: $DOMAIN_IP"
fi

# Get server's public IP
SERVER_IP=$(curl -s https://api.ipify.org)
log_info "Server's public IP: $SERVER_IP"

if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
    log_warning "Domain IP ($DOMAIN_IP) does not match server IP ($SERVER_IP)"
    log_warning "Make sure your domain is pointing to this server"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if port 80 is accessible
log_info "Checking if port 80 is accessible..."
if timeout 5 bash -c "</dev/tcp/$DOMAIN/80" 2>/dev/null; then
    log_success "Port 80 is accessible"
else
    log_warning "Port 80 may not be accessible from outside"
    log_info "Make sure your firewall allows incoming traffic on port 80"
fi

echo ""

# Step 1: Create directories
print_header "📁 Step 1: Creating directories"
mkdir -p certbot/conf certbot/www nginx/logs
log_success "Directories created"
echo ""

# Step 2: Create temporary HTTP-only nginx configuration
print_header "🔧 Step 2: Creating temporary HTTP-only nginx config"

# Backup original configuration
if [ -f "nginx/conf.d/astro.conf" ]; then
    cp nginx/conf.d/astro.conf nginx/conf.d/astro.conf.backup
    log_info "Original configuration backed up"
fi

# Create HTTP-only configuration for ACME challenge
cat > nginx/conf.d/astro.conf.http-only << 'EOF'
# Temporary HTTP-only configuration for Let's Encrypt validation
server {
    listen 80;
    listen [::]:80;
    server_name DOMAIN_PLACEHOLDER www.DOMAIN_PLACEHOLDER;

    # Let's Encrypt ACME Challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }

    # Temporary: serve simple test page
    location / {
        return 200 'Server is ready for SSL certificate validation\n';
        add_header Content-Type text/plain;
    }
}
EOF

# Replace domain placeholder
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" nginx/conf.d/astro.conf.http-only

# Use HTTP-only config temporarily
mv nginx/conf.d/astro.conf nginx/conf.d/astro.conf.ssl
cp nginx/conf.d/astro.conf.http-only nginx/conf.d/astro.conf

log_success "HTTP-only configuration created"
echo ""

# Step 3: Start nginx in HTTP-only mode
print_header "🚀 Step 3: Starting nginx (HTTP only)"
log_info "Starting nginx to serve ACME challenge..."

# Stop any existing containers
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Start only nginx
docker compose -f docker-compose.prod.yml up -d nginx

# Wait for nginx to be ready
log_info "Waiting for nginx to be ready..."
sleep 5

# Test if nginx is responding
if timeout 10 curl -f http://$DOMAIN/.well-known/acme-challenge/test 2>/dev/null; then
    log_info "Nginx is responding (404 is expected at this point)"
elif timeout 10 curl -f http://$DOMAIN/ > /dev/null 2>&1; then
    log_success "Nginx is responding"
else
    log_error "Nginx is not responding on http://$DOMAIN"
    log_info "Check nginx logs:"
    docker compose -f docker-compose.prod.yml logs nginx
    exit 1
fi

log_success "Nginx started and responding"
echo ""

# Step 4: Obtain SSL certificate
print_header "📜 Step 4: Obtaining SSL certificate from Let's Encrypt"
log_info "This may take a minute..."
log_info "If this times out, check:"
log_info "  1. DNS is pointing to this server ($SERVER_IP)"
log_info "  2. Port 80 is open in firewall"
log_info "  3. Domain is accessible: curl http://$DOMAIN"

# Run certbot with timeout
set +e  # Don't exit on error
timeout 300 docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    $STAGING_FLAG \
    -d "$DOMAIN" \
    -d "www.$DOMAIN" \
    --verbose

CERTBOT_EXIT=$?
set -e

if [ $CERTBOT_EXIT -eq 124 ]; then
    log_error "Certbot timed out after 5 minutes"
    log_info "Common causes:"
    log_info "  - Domain DNS not pointing to this server"
    log_info "  - Firewall blocking port 80"
    log_info "  - Let's Encrypt cannot reach your server"
    log_info ""
    log_info "Debug steps:"
    log_info "  1. Test from outside: curl http://$DOMAIN"
    log_info "  2. Check DNS: dig $DOMAIN"
    log_info "  3. Check firewall: sudo ufw status"
    log_info "  4. Check nginx: docker compose -f docker-compose.prod.yml logs nginx"

    # Restore original config
    if [ -f "nginx/conf.d/astro.conf.backup" ]; then
        mv nginx/conf.d/astro.conf.backup nginx/conf.d/astro.conf
    fi
    exit 1
elif [ $CERTBOT_EXIT -ne 0 ]; then
    log_error "Failed to obtain SSL certificate (exit code: $CERTBOT_EXIT)"
    log_info "Check certbot logs above for details"

    # Restore original config
    if [ -f "nginx/conf.d/astro.conf.backup" ]; then
        mv nginx/conf.d/astro.conf.backup nginx/conf.d/astro.conf
    fi
    exit 1
fi

log_success "SSL certificate obtained successfully!"
echo ""

# Step 5: Update nginx configuration with SSL
print_header "🔓 Step 5: Enabling HTTPS in nginx"
log_info "Updating nginx configuration with SSL..."

# Restore original configuration
mv nginx/conf.d/astro.conf.ssl nginx/conf.d/astro.conf

# Update domain in configuration
sed -i "s/server_name _;/server_name $DOMAIN www.$DOMAIN;/g" nginx/conf.d/astro.conf
sed -i "s|/etc/letsencrypt/live/example.com/|/etc/letsencrypt/live/$DOMAIN/|g" nginx/conf.d/astro.conf

log_success "Configuration updated"

# Restart nginx with full configuration
log_info "Restarting nginx with HTTPS enabled..."
docker compose -f docker-compose.prod.yml restart nginx

sleep 3
log_success "HTTPS enabled"
echo ""

# Step 6: Verify SSL
print_header "✅ Step 6: Verifying SSL certificate"
log_info "Checking certificate validity..."

# Check if certificate exists
if docker compose -f docker-compose.prod.yml exec -T nginx test -f /etc/letsencrypt/live/$DOMAIN/fullchain.pem; then
    log_success "Certificate files found"

    # Show certificate info
    log_info "Certificate details:"
    docker compose -f docker-compose.prod.yml exec -T certbot certbot certificates 2>/dev/null | grep -A 10 "$DOMAIN" || true
else
    log_warning "Certificate files not found in expected location"
fi

# Test HTTPS connection
log_info "Testing HTTPS connection..."
if timeout 10 curl -f -k https://$DOMAIN > /dev/null 2>&1; then
    log_success "HTTPS is working!"
else
    log_warning "Could not connect via HTTPS (may take a few seconds to propagate)"
fi

echo ""

# Step 7: Test renewal
print_header "🔄 Step 7: Testing certificate renewal"
log_info "Running dry-run renewal test..."

if timeout 120 docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run 2>/dev/null; then
    log_success "Renewal test passed! Auto-renewal is configured."
else
    log_warning "Renewal test failed or timed out. Manual renewal may be needed."
fi
echo ""

# Cleanup
log_info "Cleaning up temporary files..."
rm -f nginx/conf.d/astro.conf.http-only
rm -f nginx/conf.d/astro.conf.backup
log_success "Cleanup complete"
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
echo "2. Start all services:"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "3. Test your site:"
echo "   - https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "   - https://securityheaders.com/?q=$DOMAIN"
echo ""
echo "4. Monitor certificate expiration:"
echo "   - Certificates auto-renew every 12 hours via certbot container"
echo "   - Expires in 90 days, renews when < 30 days remaining"
echo ""

log_info "SSL certificate location:"
echo "   - Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "   - Private key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "   - Chain: /etc/letsencrypt/live/$DOMAIN/chain.pem"
echo ""

exit 0
