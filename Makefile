# Makefile — common development commands

VENV   := .venv
PYTHON := $(VENV)/bin/python

.PHONY: help \
        venv setup setup-mcp setup-full setup-prereqs setup-env setup-dirs \
        dev-local dev-docker down \
        backend backend-install \
        frontend frontend-install \
        screener-install screener-pipeline screener-scan \        llm-gateway-install llm-gateway-test llm-providers llm-benchmark \        db-local db-up db-migrate db-revision \
        test test-backend test-frontend \
        lint format \
        clean clean-cache clean-venv clean-backend clean-frontend clean-all

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────

$(VENV)/bin/activate:
	@bash setup.sh --venv

venv: $(VENV)/bin/activate ## Ensure repo-level Python venv exists

setup-full: ## Full repo setup (prereqs, venv, all deps, env files, dirs)
	@bash setup.sh

setup: venv ## Install all project dependencies into local venv + node_modules
	@bash setup.sh --backend
	@bash setup.sh --frontend
	@echo "✅ Setup complete"

setup-prereqs: ## Check/install system prerequisites (pyenv, nvm, pnpm, pdm)
	@bash setup.sh --prereqs

setup-env: ## Scaffold .env files from .env.example templates (non-destructive)
	@bash setup.sh --env

setup-dirs: ## Create all required directories (logs, screener data, models)
	@bash setup.sh --dirs

setup-mcp: ## Install Playwright MCP server for Copilot browser integration
	@echo "🌐 Installing Playwright Chromium browser..."
	npx playwright install chromium
	@echo ""
	@echo "✅ Playwright MCP ready — configured in .vscode/settings.json"
	@echo "   Restart VS Code to activate the MCP server."
	@echo "   Copilot can now open URLs, take screenshots, and inspect Chrome."

# ── Full Stack ───────────────────────────────────

dev-local: ## Start backend + frontend via Procfile (requires DB running)
	@command -v overmind >/dev/null 2>&1 && overmind start && exit 0; \
	 command -v honcho   >/dev/null 2>&1 && honcho start   && exit 0; \
	 echo "❌ Install overmind (brew install overmind) or honcho (pip install honcho)"; exit 1

dev-docker: ## Start all services with Docker/OrbStack
	docker compose -f infra/docker-compose.yml up --build

down: ## Stop Docker services
	docker compose -f infra/docker-compose.yml down

# ── Backend ──────────────────────────────────────

backend: venv ## Run backend dev server
	cd backend && pdm run dev

backend-install: venv ## Install backend Python dependencies
	@bash setup.sh --backend

# ── Frontend ─────────────────────────────────────

frontend: ## Run frontend dev server
	cd frontend && pnpm dev

frontend-install: ## Install frontend Node dependencies
	@bash setup.sh --frontend

# ── Screener ─────────────────────────────────────

screener-install: venv ## Install screener ML dependencies into .venv
	@bash setup.sh --screener

screener-pipeline: venv ## Run full screener pipeline (data → train → backtest)
	@bash setup.sh --pipeline

screener-scan: venv ## Run daily screener live scan
	@bash setup.sh --scan

# ── LLM Gateway ──────────────────────────────────

llm-gateway-install: venv ## Install llm-gateway package into .venv via PDM
	cd llm-gateway && $(PYTHON) -m pip install -e .

llm-gateway-test: venv ## Run llm-gateway test suite
	cd llm-gateway && $(PYTHON) -m pytest -v

llm-providers: venv ## Show LLM provider health and remaining quota
	$(PYTHON) -m alphaforge_llm_gateway providers

llm-benchmark: venv ## Run LLM benchmark across all providers
	$(PYTHON) -m alphaforge_llm_gateway benchmark

# ── Database / Infrastructure ────────────────────

db-local: ## Setup PostgreSQL & Redis via Homebrew (macOS, no Docker)
	@bash setup.sh --db

db-up: ## Start PostgreSQL & Redis via Docker/OrbStack
	docker compose -f infra/docker-compose.yml up postgres redis -d

db-migrate: ## Run Alembic migrations (upgrade head)
	cd backend && pdm run migrate

db-revision: ## Create a new migration  (usage: make db-revision msg="add users table")
	@test -n "$(msg)" || { echo "❌ Usage: make db-revision msg=\"describe change\""; exit 1; }
	cd backend && pdm run revision "$(msg)"

# ── Testing ──────────────────────────────────────

test: test-backend test-frontend ## Run all tests and linters

test-backend: ## Run backend tests (pytest)
	cd backend && pdm run test

test-frontend: ## Run frontend lint + type-check
	cd frontend && pnpm lint && pnpm type-check

# ── Quality ──────────────────────────────────────

lint: ## Lint everything
	cd backend && pdm run lint
	cd frontend && pnpm lint

format: ## Auto-format everything
	cd backend && pdm run format

# ── Cleanup ──────────────────────────────────────

clean: ## Remove build artifacts and bytecode (keeps venv and node_modules)
	find backend packages -type d -name __pycache__  -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .ruff_cache   -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .mypy_cache   -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/*.egg-info
	rm -rf frontend/.next
	@echo "✅ Cleaned"

clean-cache: ## Remove only tool caches (same as clean, without build artifacts)
	find backend packages -type d -name __pycache__  -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .ruff_cache   -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .mypy_cache   -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/.next frontend/node_modules/.cache
	@echo "✅ Caches cleared"

clean-venv: ## Remove the repo-level Python venv
	rm -rf $(VENV)
	@echo "✅ Venv removed"

clean-backend: ## Deep-clean backend — artifacts, caches, and venv
	find backend packages -type d -name __pycache__  -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .ruff_cache   -exec rm -rf {} + 2>/dev/null || true
	find backend packages -type d -name .mypy_cache   -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/dist backend/*.egg-info
	rm -rf $(VENV)
	@echo "✅ Backend fully cleaned"

clean-frontend: ## Deep-clean frontend — build output, cache, and node_modules
	rm -rf frontend/.next frontend/node_modules/.cache frontend/node_modules
	@echo "✅ Frontend fully cleaned"

clean-all: clean-backend clean-frontend ## Nuclear clean — removes everything (run 'make setup' to restore)
	rm -rf node_modules packages/*/node_modules
	@echo "✅ Full clean complete — run 'make setup' to restore"
