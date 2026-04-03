# Makefile — common development commands

.PHONY: help dev-local dev-docker backend frontend db-up db-local db-migrate test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Full Stack ───────────────────────────────────

dev-local: ## Start backend + frontend locally (requires brew services for DB)
	@command -v overmind >/dev/null 2>&1 && overmind start || \
	(command -v honcho >/dev/null 2>&1 && honcho start || \
	echo "Install overmind (brew install overmind) or honcho (pip install honcho)")

dev-docker: ## Start all services with Docker/OrbStack
	docker compose -f infra/docker-compose.yml up --build

down: ## Stop Docker services
	docker compose -f infra/docker-compose.yml down

# ── Backend ──────────────────────────────────────

backend: ## Run backend locally
	cd backend && pdm run dev

backend-install: ## Install backend dependencies (pdm + uv)
	cd backend && pdm install

# ── Frontend ─────────────────────────────────────

frontend: ## Run frontend locally
	cd frontend && pnpm dev

frontend-install: ## Install frontend dependencies (pnpm)
	cd frontend && pnpm install

# ── Database / Infrastructure ────────────────────

db-local: ## Setup PostgreSQL & Redis via Homebrew (macOS, no Docker)
	bash infra/setup-local.sh

db-up: ## Start just PostgreSQL & Redis via Docker/OrbStack
	docker compose -f infra/docker-compose.yml up postgres redis -d

db-migrate: ## Run Alembic migrations
	cd backend && pdm run migrate

db-revision: ## Create new migration (usage: make db-revision msg="add users table")
	cd backend && pdm run revision "$(msg)"

# ── Testing ──────────────────────────────────────

test: ## Run all tests
	cd backend && pdm run test
	cd frontend && pnpm lint

test-backend: ## Run backend tests only
	cd backend && pdm run test

# ── Quality ──────────────────────────────────────

lint: ## Lint everything
	cd backend && pdm run lint
	cd frontend && pnpm lint

format: ## Auto-format everything
	cd backend && pdm run format

# ── Cleanup ──────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/*.egg-info
	rm -rf frontend/.next frontend/node_modules/.cache
