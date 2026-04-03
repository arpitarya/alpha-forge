# Makefile — common development commands

.PHONY: help dev backend frontend db-up db-migrate test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Full Stack ───────────────────────────────────

dev: ## Start all services with Docker Compose
	docker compose up --build

down: ## Stop all services
	docker compose down

# ── Backend ──────────────────────────────────────

backend: ## Run backend locally (requires venv)
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-install: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

# ── Frontend ─────────────────────────────────────

frontend: ## Run frontend locally
	cd frontend && npm run dev

frontend-install: ## Install frontend dependencies
	cd frontend && npm install

# ── Database ─────────────────────────────────────

db-up: ## Start just PostgreSQL & Redis
	docker compose up postgres redis -d

db-migrate: ## Run Alembic migrations
	cd backend && alembic upgrade head

db-revision: ## Create new migration (usage: make db-revision msg="add users table")
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ── Testing ──────────────────────────────────────

test: ## Run all tests
	cd backend && pytest -v --tb=short
	cd frontend && npm run lint

test-backend: ## Run backend tests only
	cd backend && pytest -v --tb=short

# ── Quality ──────────────────────────────────────

lint: ## Lint everything
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run lint

format: ## Auto-format everything
	cd backend && ruff format .

# ── Cleanup ──────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/*.egg-info
	rm -rf frontend/.next frontend/node_modules/.cache
