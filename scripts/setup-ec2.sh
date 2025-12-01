#!/bin/bash

# setup-ec2.sh - One-time EC2 instance setup for Real Astrology application
# Run this script on a fresh EC2 instance to prepare it for deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/astro-natal-chart"
REPO_URL="https://github.com/lmeazzini/astro-natal-chart.git"

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

print_header "🚀 Real Astrology - EC2 Instance Setup"
log_info "This script will prepare your EC2 instance for deployment"
log_warning "This should only be run once on a fresh instance"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Please do not run this script as root"
    log_info "Run as: bash setup-ec2.sh"
    exit 1
fi

# ============================================
# 1. System update
# ============================================
print_header "1️⃣  Updating System Packages"
log_info "Updating package lists..."
sudo apt update

log_info "Upgrading installed packages (this may take a few minutes)..."
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y

log_success "System packages updated"

# ============================================
# 2. Install Docker
# ============================================
print_header "2️⃣  Installing Docker"

if command -v docker &> /dev/null; then
    log_warning "Docker is already installed"
    docker --version
else
    log_info "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh

    # Add current user to docker group
    sudo usermod -aG docker $USER
    log_success "Docker installed successfully"
    docker --version
fi

# ============================================
# 3. Install Docker Compose
# ============================================
print_header "3️⃣  Installing Docker Compose"

if docker compose version &> /dev/null; then
    log_warning "Docker Compose is already installed"
    docker compose version
else
    log_info "Installing Docker Compose plugin..."
    sudo apt install -y docker-compose-plugin
    log_success "Docker Compose installed successfully"
    docker compose version
fi

# ============================================
# 4. Install additional tools
# ============================================
print_header "4️⃣  Installing Additional Tools"

log_info "Installing Git, Make, Curl, and other utilities..."
sudo apt install -y git make curl wget vim htop

log_success "Additional tools installed"

# ============================================
# 5. Create application directory
# ============================================
print_header "5️⃣  Creating Application Directory"

if [ -d "$APP_DIR" ]; then
    log_warning "Application directory already exists: $APP_DIR"
else
    log_info "Creating application directory..."
    sudo mkdir -p "$APP_DIR"
    sudo chown $USER:$USER "$APP_DIR"
    log_success "Application directory created: $APP_DIR"
fi

# ============================================
# 6. Clone repository
# ============================================
print_header "6️⃣  Cloning Repository"

cd "$APP_DIR"

if [ -d ".git" ]; then
    log_warning "Repository already cloned"
    log_info "Current branch: $(git branch --show-current)"
    log_info "Latest commit: $(git log -1 --oneline)"
else
    log_info "Cloning repository from $REPO_URL..."
    git clone "$REPO_URL" .
    log_success "Repository cloned successfully"
fi

# Configure git
git config pull.rebase false

# ============================================
# 7. Create directory structure
# ============================================
print_header "7️⃣  Creating Directory Structure"

log_info "Creating required directories..."
mkdir -p backups
mkdir -p logs
mkdir -p apps/api/media
mkdir -p apps/api/media/pdfs

log_success "Directory structure created"

# ============================================
# 8. Environment files setup
# ============================================
print_header "8️⃣  Environment Files Setup"

log_info "Creating environment files from examples..."

# Backend .env
if [ -f "apps/api/.env" ]; then
    log_warning "Backend .env already exists - skipping"
else
    cp apps/api/.env.example apps/api/.env
    log_success "Created apps/api/.env from example"
    log_warning "⚠️  IMPORTANT: Edit apps/api/.env with your production values!"
fi

# Frontend .env
if [ -f "apps/web/.env" ]; then
    log_warning "Frontend .env already exists - skipping"
else
    cp apps/web/.env.example apps/web/.env
    log_success "Created apps/web/.env from example"
    log_warning "⚠️  IMPORTANT: Edit apps/web/.env with your production values!"
fi

# ============================================
# 9. Docker group activation
# ============================================
print_header "9️⃣  Finalizing Docker Setup"

log_warning "Docker group membership requires re-login to take effect"
log_info "Testing Docker access..."

if docker ps &> /dev/null; then
    log_success "Docker is accessible"
else
    log_warning "Docker requires re-login to work without sudo"
    log_info "After this script completes, run: newgrp docker"
fi

# ============================================
# 10. Summary and next steps
# ============================================
print_header "✅ EC2 Setup Complete!"

log_success "Your EC2 instance is now prepared for deployment"
echo ""

log_info "📋 Next Steps:"
echo ""
echo "  1. Configure environment variables:"
echo "     nano $APP_DIR/apps/api/.env"
echo ""
echo "  2. Important variables to set:"
echo "     - DOMAIN=your-domain.com"
echo "     - POSTGRES_PASSWORD=<strong-password>"
echo "     - REDIS_PASSWORD=<strong-password>"
echo "     - SECRET_KEY=<generate with: openssl rand -hex 32>"
echo "     - ALLOWED_ORIGINS=https://your-domain.com"
echo "     - AWS credentials (S3)"
echo "     - OAuth credentials (Google, GitHub, Facebook)"
echo "     - OpenAI API key (optional)"
echo "     - SMTP credentials (optional)"
echo ""
echo "  3. Setup SSL certificates:"
echo "     cd $APP_DIR"
echo "     bash scripts/setup-ssl.sh"
echo ""
echo "  4. Run first deployment:"
echo "     cd $APP_DIR"
echo "     docker compose -f docker-compose.prod.yml build"
echo "     docker compose -f docker-compose.prod.yml up -d"
echo "     docker compose -f docker-compose.prod.yml exec api uv run alembic upgrade head"
echo ""
echo "  5. Verify deployment:"
echo "     docker compose -f docker-compose.prod.yml ps"
echo "     curl http://localhost/health"
echo ""
echo "  6. Configure GitHub Actions secrets:"
echo "     - EC2_HOST=<your-elastic-ip>"
echo "     - EC2_USER=ubuntu"
echo "     - EC2_SSH_KEY=<your-private-key>"
echo "     - DOMAIN=your-domain.com"
echo ""

log_warning "⚠️  Important Security Notes:"
echo "  - Change all default passwords"
echo "  - Use strong passwords for PostgreSQL and Redis"
echo "  - Keep your .env files secure (never commit to git)"
echo "  - Configure firewall rules (only 80, 443, 22 should be open)"
echo "  - Setup automated backups (cron job for backup-db.sh)"
echo ""

log_info "For full documentation, see: $APP_DIR/docs/DEPLOY_GUIDE.md"
echo ""

# Check if relogin is needed
if ! docker ps &> /dev/null; then
    log_warning "🔄 Docker group activation required"
    log_info "Run: newgrp docker"
    echo ""
fi

log_success "Setup complete! 🎉"
