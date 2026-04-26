# Local Development — Process Manager
# Usage: brew install overmind && overmind start
# Or:    pip install honcho && honcho start
# Or:    foreman start (if you have Ruby)

# ── Database Management (run separately) ─────────
# just db-start    # Start PostgreSQL + Redis
# just db-stop     # Stop PostgreSQL + Redis
# just db-restart  # Restart both services
# just db-status   # Check service status

backend: cd backend && pdm run dev
frontend: cd frontend && pnpm dev
