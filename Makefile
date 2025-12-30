.PHONY: help install dev build test clean docker-up docker-down docker-logs migrate migrate-status migrate-check

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo '${GREEN}Available commands:${NC}'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${YELLOW}%-20s${NC} %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "${GREEN}Installing dependencies...${NC}"
	npm install
	cd apps/api && pip install -r requirements.txt
	cd apps/web && npm install

dev: ## Start development environment
	@echo "${GREEN}Starting development servers...${NC}"
	npm run dev

build: ## Build all apps for production
	@echo "${GREEN}Building all apps...${NC}"
	npm run build

test: ## Run all tests
	@echo "${GREEN}Running tests...${NC}"
	npm run test

lint: ## Lint all code
	@echo "${GREEN}Linting code...${NC}"
	npm run lint

format: ## Format all code
	@echo "${GREEN}Formatting code...${NC}"
	npm run format

clean: ## Clean all build artifacts and dependencies
	@echo "${GREEN}Cleaning...${NC}"
	npm run clean
	rm -rf apps/api/__pycache__ apps/api/.pytest_cache apps/api/htmlcov
	rm -rf apps/web/dist apps/web/node_modules

# Docker commands
docker-up: ## Start all Docker services
	@echo "${GREEN}Starting Docker services...${NC}"
	docker-compose up -d

docker-down: ## Stop all Docker services
	@echo "${GREEN}Stopping Docker services...${NC}"
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-restart: ## Restart all Docker services
	@echo "${GREEN}Restarting Docker services...${NC}"
	docker-compose restart

docker-rebuild: ## Rebuild and restart Docker services
	@echo "${GREEN}Rebuilding Docker services...${NC}"
	docker-compose up -d --build

# Database commands
migrate: ## Run database migrations
	@echo "${GREEN}Running migrations...${NC}"
	cd apps/api && alembic upgrade head

migrate-create: ## Create a new migration
	@echo "${GREEN}Creating migration...${NC}"
	@read -p "Enter migration name: " name; \
	cd apps/api && alembic revision --autogenerate -m "$$name"

migrate-down: ## Rollback last migration
	@echo "${GREEN}Rolling back migration...${NC}"
	cd apps/api && alembic downgrade -1

migrate-status: ## Show current migration state
	@echo "${GREEN}Migration Status:${NC}"
	@echo "Current revision:"
	@docker compose exec api uv run alembic current
	@echo "\nRecent history:"
	@docker compose exec api uv run alembic history -v | head -20

migrate-check: ## Verify migration health (run before production deploy)
	@echo "${GREEN}Running migration health check...${NC}"
	./scripts/check-migrations.sh

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "${YELLOW}WARNING: This will destroy all database data!${NC}"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose up -d db redis; \
		sleep 5; \
		cd apps/api && alembic upgrade head; \
	fi

# API commands
api-shell: ## Open Python shell in API container
	docker-compose exec api python

api-logs: ## Show API logs
	docker-compose logs -f api

api-test: ## Run API tests
	cd apps/api && pytest

# Web commands
web-shell: ## Open shell in Web container
	docker-compose exec web sh

web-logs: ## Show Web logs
	docker-compose logs -f web

web-test: ## Run Web tests
	cd apps/web && npm run test

# Production commands
prod-build: ## Build for production
	@echo "${GREEN}Building for production...${NC}"
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production environment
	@echo "${GREEN}Starting production environment...${NC}"
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down
