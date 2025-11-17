#!/bin/bash

# Complete System Reboot Script
# This script stops, rebuilds, and restarts all Docker services

set -e  # Exit on error

echo "🔄 Starting complete system reboot..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Stop all services
echo -e "${YELLOW}Step 1/7: Stopping all Docker services...${NC}"
docker compose down
echo -e "${GREEN}✅ Services stopped${NC}"
echo ""

# Step 2: Clean up dangling images and containers
echo -e "${YELLOW}Step 2/7: Cleaning up dangling containers and images...${NC}"
docker system prune -f
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Step 3: Rebuild images
echo -e "${YELLOW}Step 3/7: Rebuilding Docker images...${NC}"
docker compose build --no-cache
echo -e "${GREEN}✅ Images rebuilt${NC}"
echo ""

# Step 4: Start all services
echo -e "${YELLOW}Step 4/7: Starting all services...${NC}"
docker compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 5: Wait for services to be ready
echo -e "${YELLOW}Step 5/7: Waiting for services to be ready...${NC}"
echo "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U astro > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ PostgreSQL failed to start${NC}"
        exit 1
    fi
    sleep 1
done

echo "Waiting for API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ API failed to start${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Step 6: Run database migrations
echo -e "${YELLOW}Step 6/7: Running database migrations...${NC}"
docker compose exec -T api alembic upgrade head
echo -e "${GREEN}✅ Migrations complete${NC}"
echo ""

# Step 7: Display service status
echo -e "${YELLOW}Step 7/7: Verifying service status...${NC}"
docker compose ps
echo ""

# Health checks
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 System reboot complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📡 Service URLs:${NC}"
echo -e "  🌐 Frontend:     ${GREEN}http://localhost:5173${NC}"
echo -e "  🔧 API:          ${GREEN}http://localhost:8000${NC}"
echo -e "  📚 Swagger Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  🗄️  PostgreSQL:   ${GREEN}localhost:5432${NC}"
echo -e "  📦 Redis:        ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${BLUE}💡 Useful commands:${NC}"
echo -e "  📋 View logs:         ${YELLOW}docker compose logs -f${NC}"
echo -e "  📋 View API logs:     ${YELLOW}docker compose logs -f api${NC}"
echo -e "  📋 View Web logs:     ${YELLOW}docker compose logs -f web${NC}"
echo -e "  ⏸️  Stop services:     ${YELLOW}docker compose down${NC}"
echo -e "  ▶️  Restart service:   ${YELLOW}docker compose restart <service>${NC}"
echo ""

# Final health check
echo -e "${BLUE}🏥 Health Check:${NC}"
API_HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"' || echo "")
if [ -n "$API_HEALTH" ]; then
    echo -e "  API Status: ${GREEN}✅ Healthy${NC}"
else
    echo -e "  API Status: ${RED}❌ Unhealthy${NC}"
fi
echo ""
