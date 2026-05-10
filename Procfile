# Local Development — Process Manager
# Usage: brew install overmind && overmind start
# Or:    pip install honcho && honcho start
# Or:    foreman start (if you have Ruby)
#
# Ports come from .env.port — overmind/honcho auto-load it via OVERMIND_ENV/.env.
# If your runner doesn't pick it up, run:  set -a && source .env.port && overmind start
#
# ── Database Management (run separately) ─────────
# just db-start    # Start PostgreSQL + Redis
# just db-stop     # Stop PostgreSQL + Redis
# just db-restart  # Restart both services
# just db-status   # Check service status

backend: bash -c 'set -a && source .env.port && set +a && cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT"'
frontend: bash -c 'set -a && source .env.port && set +a && cd frontend && pnpm dev'
