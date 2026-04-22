## justfile — common development commands

venv  := ".venv"
python := venv / "bin/python"

# Show this help
default:
    @just --list

# ── Setup ────────────────────────────────────────

# Ensure repo-level Python venv exists
venv:
    bash setup.sh --venv

# Full repo setup (prereqs, venv, all deps, env files, dirs)
setup-full:
    bash setup.sh

# Install all project dependencies into local venv + node_modules
setup: venv
    bash setup.sh --backend
    bash setup.sh --frontend
    @echo "✅ Setup complete"

# Check/install system prerequisites (pyenv, nvm, pnpm, pdm)
setup-prereqs:
    bash setup.sh --prereqs

# Scaffold .env files from .env.example templates (non-destructive)
setup-env:
    bash setup.sh --env

# Create all required directories (logs, screener data, models)
setup-dirs:
    bash setup.sh --dirs

# Install Playwright MCP server for Copilot browser integration
setup-mcp:
    @echo "🌐 Installing Playwright Chromium browser..."
    npx playwright install chromium
    @echo ""
    @echo "✅ Playwright MCP ready — configured in .vscode/settings.json"
    @echo "   Restart VS Code to activate the MCP server."
    @echo "   Copilot can now open URLs, take screenshots, and inspect Chrome."

# ── Full Stack ───────────────────────────────────

# Start backend + frontend via Procfile (requires DB running)
dev-local:
    #!/usr/bin/env bash
    if command -v overmind >/dev/null 2>&1; then
        overmind start
    elif command -v honcho >/dev/null 2>&1; then
        honcho start
    else
        echo "❌ Install overmind (brew install overmind) or honcho (pip install honcho)"
        exit 1
    fi

# Start all services with Docker/OrbStack
dev-docker:
    docker compose -f infra/docker-compose.yml up --build

# Stop Docker services
down:
    docker compose -f infra/docker-compose.yml down

# ── Backend ──────────────────────────────────────

# Run backend dev server
backend: venv
    cd backend && pdm run dev

# Install backend Python dependencies
backend-install: venv
    bash setup.sh --backend

# ── Frontend ─────────────────────────────────────

# Run frontend dev server
frontend:
    cd frontend && pnpm dev

# Install frontend Node dependencies
frontend-install:
    bash setup.sh --frontend

# ── Screener ─────────────────────────────────────

# Install screener ML dependencies into .venv
screener-install: venv
    bash setup.sh --screener

# Run full screener pipeline (data → train → backtest)
screener-pipeline: venv
    bash setup.sh --pipeline

# Run daily screener live scan
screener-scan: venv
    bash setup.sh --scan

# ── LLM Gateway ──────────────────────────────────

# Install llm-gateway package into .venv via PDM
llm-gateway-install: venv
    cd llm-gateway && {{python}} -m pip install -e .

# Run llm-gateway test suite
llm-gateway-test: venv
    cd llm-gateway && {{python}} -m pytest -v

# Show LLM provider health and remaining quota
llm-providers: venv
    {{python}} -m alphaforge_llm_gateway providers

# Run LLM benchmark across all providers
llm-benchmark: venv
    {{python}} -m alphaforge_llm_gateway benchmark

# ── Database / Infrastructure ────────────────────

# Setup PostgreSQL & Redis via Homebrew (macOS, no Docker)
db-local:
    bash setup.sh --db

# Start PostgreSQL & Redis via Docker/OrbStack
db-up:
    docker compose -f infra/docker-compose.yml up postgres redis -d

# Run Alembic migrations (upgrade head)
db-migrate:
    cd backend && pdm run migrate

# Create a new migration  (usage: just db-revision "add users table")
db-revision msg:
    cd backend && pdm run revision "{{msg}}"

# ── Testing ──────────────────────────────────────

# Run all tests and linters
test: test-backend test-frontend

# Run backend tests (pytest)
test-backend:
    cd backend && pdm run test

# Run frontend lint + type-check
test-frontend:
    cd frontend && pnpm lint && pnpm type-check

# ── Quality ──────────────────────────────────────

# Lint everything
lint:
    cd backend && pdm run lint
    cd frontend && pnpm lint

# Auto-format everything
format:
    cd backend && pdm run format

# ── Cleanup ──────────────────────────────────────

# Remove build artifacts and bytecode (keeps venv and node_modules)
clean:
    bash clean.sh

# Remove only tool caches
clean-cache:
    bash clean.sh --cache

# Remove the repo-level Python venv
clean-venv:
    bash clean.sh --venv

# Deep-clean backend — artifacts, caches, and venv
clean-backend:
    bash clean.sh --backend

# Deep-clean frontend — build output, cache, and node_modules
clean-frontend:
    bash clean.sh --frontend

# Nuclear clean — removes everything (run 'just setup' to restore)
clean-all:
    bash clean.sh --all
