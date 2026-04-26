#!/bin/bash
# AlphaForge — Database Start/Stop Control Script
# Manages PostgreSQL 16 + Redis via Homebrew (macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# ── Colors ───────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ── Helpers ──────────────────────────────────────
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# ── Check Platform ──────────────────────────────
if [[ "$(uname)" != "Darwin" ]]; then
    log_error "This script is for macOS only. Use Docker instead:"
    echo "  docker compose -f infra/docker-compose.yml up postgres redis -d"
    exit 1
fi

# ── Check Homebrew ──────────────────────────────
if ! command -v brew &> /dev/null; then
    log_error "Homebrew not found. Install from https://brew.sh"
    exit 1
fi

# ── Commands ─────────────────────────────────────

start_db() {
    log_info "Starting PostgreSQL 16..."
    if brew services start postgresql@16 > /dev/null 2>&1; then
        log_success "PostgreSQL started"
    else
        log_warn "PostgreSQL already running or startup failed"
    fi

    log_info "Starting Redis..."
    if brew services start redis > /dev/null 2>&1; then
        log_success "Redis started"
    else
        log_warn "Redis already running or startup failed"
    fi

    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    for i in {1..10}; do
        if pg_isready -q 2>/dev/null; then
            log_success "PostgreSQL is ready"
            break
        fi
        if [[ $i -eq 10 ]]; then
            log_warn "PostgreSQL took too long to start"
        fi
        sleep 1
    done

    log_success "Database services running"
    echo ""
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis:      localhost:6379"
    echo ""
}

stop_db() {
    log_info "Stopping PostgreSQL 16..."
    if brew services stop postgresql@16 > /dev/null 2>&1; then
        log_success "PostgreSQL stopped"
    else
        log_warn "PostgreSQL already stopped or stop failed"
    fi

    log_info "Stopping Redis..."
    if brew services stop redis > /dev/null 2>&1; then
        log_success "Redis stopped"
    else
        log_warn "Redis already stopped or stop failed"
    fi

    log_success "Database services stopped"
}

status_db() {
    echo ""
    echo -e "${BLUE}Database Service Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # PostgreSQL
    if brew services list 2>/dev/null | grep -q "postgresql@16.*started"; then
        log_success "PostgreSQL 16 is running"
        pg_isready 2>/dev/null && echo "              Connection: OK" || echo "              Connection: FAILED"
    else
        log_warn "PostgreSQL 16 is stopped"
    fi

    # Redis
    if brew services list 2>/dev/null | grep -q "redis.*started"; then
        log_success "Redis is running"
        redis-cli ping > /dev/null 2>&1 && echo "         Connection: OK" || echo "         Connection: FAILED"
    else
        log_warn "Redis is stopped"
    fi

    echo ""
}

restart_db() {
    log_info "Restarting database services..."
    stop_db
    echo ""
    start_db
}

# ── Main ─────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 {start|stop|restart|status}"
    echo ""
    echo "Commands:"
    echo "  start   - Start PostgreSQL and Redis"
    echo "  stop    - Stop PostgreSQL and Redis"
    echo "  restart - Restart PostgreSQL and Redis"
    echo "  status  - Show service status"
    exit 0
fi

case "$1" in
    start)
        start_db
        ;;
    stop)
        stop_db
        ;;
    restart)
        restart_db
        ;;
    status)
        status_db
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
