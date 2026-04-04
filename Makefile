# Makefile — common development commands

VENV       := .venv
PYTHON     := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
ACTIVATE   := source $(VENV)/bin/activate

.PHONY: help setup dev-local dev-docker backend frontend db-up db-local db-migrate test lint clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Setup ────────────────────────────────────────

$(VENV)/bin/activate: ## Create repo-level Python venv (uses .python-version)
	@PYTHON_VER=$$(cat .python-version 2>/dev/null || echo "3.14.2"); \
	PYENV_PYTHON="$$(pyenv root)/versions/$$PYTHON_VER/bin/python"; \
	if [ -x "$$PYENV_PYTHON" ]; then \
		echo "Creating venv with pyenv Python $$PYTHON_VER..."; \
		$$PYENV_PYTHON -m venv $(VENV); \
	elif command -v python$$PYTHON_VER >/dev/null 2>&1; then \
		echo "Creating venv with python$$PYTHON_VER..."; \
		python$$PYTHON_VER -m venv $(VENV); \
	else \
		echo "❌ Python $$PYTHON_VER not found. Install via pyenv: pyenv install $$PYTHON_VER"; \
		exit 1; \
	fi
	@echo "✅ Venv created at $(VENV) ($$($(PYTHON) --version))"

venv: $(VENV)/bin/activate ## Ensure repo-level venv exists

setup: venv ## Install all project dependencies (no global installs)
	@echo "📦 Installing backend dependencies (PDM → .venv)..."
	cd backend && pdm install
	@echo ""
	@echo "📦 Installing workspace Node packages (pnpm)..."
	pnpm install
	@echo ""
	@echo "🔍 Checking required CLI tools..."
	@ok=1; \
	command -v pnpm  >/dev/null 2>&1 && echo "  ✅ pnpm $$(pnpm -v)"          || { echo "  ❌ pnpm  — install via: corepack enable && corepack prepare pnpm@latest --activate"; ok=0; }; \
	command -v pdm   >/dev/null 2>&1 && echo "  ✅ pdm $$(pdm --version)"      || { echo "  ❌ pdm   — install via: brew install pdm  (or pipx install pdm)"; ok=0; }; \
	command -v overmind >/dev/null 2>&1 && echo "  ✅ overmind"                  || echo "  ⚠️  overmind — optional, install via: brew install overmind"; \
	echo ""; \
	if [ $$ok -eq 1 ]; then echo "✅ Setup complete!"; else echo "⚠️  Fix the missing tools above, then re-run make setup"; fi

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

backend: venv ## Run backend locally
	cd backend && pdm run dev

backend-install: venv ## Install backend dependencies (pdm → root .venv)
	cd backend && pdm install
	@echo "✅ Backend deps installed into .venv"

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

clean-venv: ## Remove the repo-level venv entirely
	rm -rf $(VENV)
