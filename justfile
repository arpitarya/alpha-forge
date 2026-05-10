## justfile — common development commands

# Load port numbers from .env.port (BACKEND_PORT, FRONTEND_PORT, ...)
set dotenv-load := true
set dotenv-filename := ".env.port"

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
setup:
    bash setup.sh
    @echo "✅ Setup complete"

# Check/install system prerequisites (pyenv, nvm, pnpm, uv)
setup-prereqs:
    bash setup.sh --prereqs

# Scaffold .env files from .env.example templates (non-destructive)
setup-env:
    bash setup.sh --env

# Sync .env files from .env.example templates + auto-generate blank secrets (idempotent)
setup-config:
    bash setup-config.sh

# Preview what setup-config would change without writing
setup-config-check:
    bash setup-config.sh --check

# Sync env keys only — skip secret auto-generation
setup-config-keys:
    bash setup-config.sh --no-secrets

# Create all required directories (logs, screener data, models)
setup-dirs:
    bash setup.sh --dirs

# Setup graphify for Claude, Codex, Copilot, git hooks, and graph output
graphify-setup:
    bash setup.sh --graphify

# Refresh graphify-out after code changes
graphify-update:
    graphify update .

# Check whether graphify needs a semantic refresh
graphify-check:
    graphify check-update .

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
    docker compose --env-file .env.port -f infra/docker-compose.yml up --build

# Stop Docker services
down:
    docker compose --env-file .env.port -f infra/docker-compose.yml down

# ── Python Workspace (uv) ────────────────────────

# Sync the entire Python workspace (backend + screener + llm-gateway + logger-py)
sync:
    uv sync

# Add a dependency to a workspace member  (usage: just add backend httpx)
add member pkg:
    cd {{member}} && uv add {{pkg}}

# Lock without installing (refresh uv.lock only)
lock:
    uv lock

# ── Backend ──────────────────────────────────────

# Run backend dev server
backend:
    cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT}

# Run backend under debugpy (VS Code attaches via "Backend: Attach (debugpy on :5678)")
backend-debug port="5678":
    @echo "🐛 Backend waiting for debugger on 127.0.0.1:{{port}} — attach in VS Code"
    cd backend && uv run python -m debugpy --listen 127.0.0.1:{{port}} --wait-for-client \
        -m uvicorn app.main:app --reload --host 0.0.0.0 --port ${BACKEND_PORT}

# Install backend Python dependencies (alias — `just sync` is the primary entry point now)
backend-install:
    bash setup.sh --backend

# ── Frontend ─────────────────────────────────────

# Run frontend dev server
frontend:
    cd frontend && pnpm dev

# Install frontend Node dependencies
frontend-install:
    bash setup.sh --frontend

# ── Screener ─────────────────────────────────────

# (install handled by `just sync` — screener is a workspace member)

# Run full screener pipeline (data → train → backtest)
screener-pipeline:
    bash setup.sh --pipeline

# Run daily screener live scan
screener-scan:
    bash setup.sh --scan

# ── Brokers ──────────────────────────────────────

# Launch Chrome with CDP debugging port for Zerodha login (one-time per session).
# Log in to kite.zerodha.com inside this window, then run `just zerodha-dump`.
zerodha-chrome:
    @echo "🌐 Launching Chrome with CDP port 9299 (loopback only)..."
    @mkdir -p "$HOME/.cache/alphaforge-chrome"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
        --remote-debugging-port=9299 \
        --remote-debugging-address=127.0.0.1 \
        --user-data-dir="$HOME/.cache/alphaforge-chrome" \
        https://kite.zerodha.com/ &

# Dump today's Zerodha holdings to ~/.alphaforge/portfolio-dumps/*.xlsx
# (waits for manual login in the CDP-attached Chrome if no cached session).
zerodha-dump:
    cd backend && uv run python -m app.modules.brokers.zerodha_dump

# Force fresh login (clears cached enctoken, then dumps).
zerodha-dump-force:
    cd backend && uv run python -m app.modules.brokers.zerodha_dump --force-login

# ── LLM Gateway ──────────────────────────────────

# (install handled by `just sync` — the workspace pulls llm-gateway as an editable member)

# Run llm-gateway test suite
llm-gateway-test:
    cd llm-gateway && uv run pytest -v

# Show LLM provider health and remaining quota
llm-providers:
    uv run python -m alphaforge_llm_gateway providers

# Run LLM benchmark across all providers
llm-benchmark:
    uv run python -m alphaforge_llm_gateway benchmark

# ── Database / Infrastructure ────────────────────

# Setup PostgreSQL & Redis via Homebrew (macOS, no Docker)
db-local:
    bash setup.sh --db

# Start PostgreSQL & Redis (Homebrew)
db-start:
    bash database/db.sh start

# Stop PostgreSQL & Redis (Homebrew)
db-stop:
    bash database/db.sh stop

# Restart PostgreSQL & Redis (Homebrew)
db-restart:
    bash database/db.sh restart

# Show PostgreSQL & Redis status
db-status:
    bash database/db.sh status

# Start PostgreSQL & Redis via Docker/OrbStack
db-up:
    docker compose --env-file .env.port -f infra/docker-compose.yml up postgres redis -d

# Run Alembic migrations (upgrade head)
db-migrate:
    cd backend && uv run alembic upgrade head

# Create a new migration  (usage: just db-revision "add users table")
db-revision msg:
    cd backend && uv run alembic revision --autogenerate -m "{{msg}}"

# ── Testing ──────────────────────────────────────

# Run all tests and linters
test: test-backend test-frontend

# Run backend tests (pytest)
test-backend:
    cd backend && uv run pytest -v --tb=short

# Run frontend lint + type-check
test-frontend:
    cd frontend && pnpm lint && pnpm type-check

# ── Quality ──────────────────────────────────────

# Lint everything
lint:
    uv run ruff check .
    cd frontend && pnpm lint

# Auto-format everything
format:
    uv run ruff format .

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
