#!/bin/bash

# Script to verify installation and setup
# Run: bash scripts/check-setup.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Astro Natal Chart - Setup Verification${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Check Node.js
echo -e "${YELLOW}Checking prerequisites...${NC}\n"

if command_exists node; then
    NODE_VERSION=$(node -v)
    print_status 0 "Node.js installed: $NODE_VERSION"
else
    print_status 1 "Node.js NOT installed"
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm -v)
    print_status 0 "npm installed: $NPM_VERSION"
else
    print_status 1 "npm NOT installed"
fi

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    print_status 0 "$PYTHON_VERSION installed"
else
    print_status 1 "Python NOT installed"
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_status 0 "$DOCKER_VERSION installed"
else
    print_status 1 "Docker NOT installed (optional but recommended)"
fi

# Check Docker Compose
if command_exists docker-compose; then
    DOCKER_COMPOSE_VERSION=$(docker-compose --version)
    print_status 0 "$DOCKER_COMPOSE_VERSION installed"
else
    print_status 1 "Docker Compose NOT installed (optional but recommended)"
fi

echo ""

# Check project structure
echo -e "${YELLOW}Checking project structure...${NC}\n"

check_file() {
    if [ -f "$1" ]; then
        print_status 0 "$1 exists"
        return 0
    else
        print_status 1 "$1 missing"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        print_status 0 "$1/ exists"
        return 0
    else
        print_status 1 "$1/ missing"
        return 1
    fi
}

# Check root files
check_file "package.json"
check_file "turbo.json"
check_file "docker-compose.yml"
check_file "PROJECT_SPEC.md"
check_file "README.md"

echo ""

# Check apps
check_dir "apps/api"
check_dir "apps/web"
check_file "apps/api/requirements.txt"
check_file "apps/api/app/main.py"
check_file "apps/web/package.json"
check_file "apps/web/src/App.tsx"

echo ""

# Check environment files
echo -e "${YELLOW}Checking environment configuration...${NC}\n"

if [ -f "apps/api/.env" ]; then
    print_status 0 "Backend .env configured"
else
    print_status 1 "Backend .env missing (copy from .env.example)"
fi

if [ -f "apps/web/.env" ]; then
    print_status 0 "Frontend .env configured"
else
    print_status 1 "Frontend .env missing (copy from .env.example)"
fi

echo ""

# Check Docker services (if running)
echo -e "${YELLOW}Checking Docker services...${NC}\n"

if command_exists docker-compose; then
    if docker-compose ps | grep -q "Up"; then
        print_status 0 "Docker Compose services running"

        # Check individual services
        if docker-compose ps db | grep -q "Up"; then
            print_status 0 "PostgreSQL (db) running"
        else
            print_status 1 "PostgreSQL (db) not running"
        fi

        if docker-compose ps redis | grep -q "Up"; then
            print_status 0 "Redis running"
        else
            print_status 1 "Redis not running"
        fi

        if docker-compose ps api | grep -q "Up"; then
            print_status 0 "FastAPI (api) running"
        else
            print_status 1 "FastAPI (api) not running"
        fi

        if docker-compose ps web | grep -q "Up"; then
            print_status 0 "React (web) running"
        else
            print_status 1 "React (web) not running"
        fi
    else
        print_status 1 "Docker Compose services not running (run: docker-compose up -d)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not available"
fi

echo ""

# Check endpoints (if services are running)
echo -e "${YELLOW}Checking API endpoints...${NC}\n"

if command_exists curl; then
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status 0 "Backend API responding (http://localhost:8000)"
    else
        print_status 1 "Backend API not responding (http://localhost:8000)"
    fi

    # Check frontend
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_status 0 "Frontend responding (http://localhost:5173)"
    else
        print_status 1 "Frontend not responding (http://localhost:5173)"
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not available, skipping endpoint checks"
fi

echo ""

# Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup verification complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "Next steps:"
echo -e "  1. If Docker services are not running: ${YELLOW}docker-compose up -d${NC}"
echo -e "  2. Run migrations: ${YELLOW}docker-compose exec api alembic upgrade head${NC}"
echo -e "  3. Access frontend: ${YELLOW}http://localhost:5173${NC}"
echo -e "  4. Access API docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "\nFor more information, see: ${YELLOW}GETTING_STARTED.md${NC}\n"
