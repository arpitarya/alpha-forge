#!/usr/bin/env bash
# ==============================================================================
# AlphaForge — Cleanup Script
# ==============================================================================
#
# Usage:
#   ./clean.sh                  # Remove build artifacts and bytecode (keeps venv + node_modules)
#   ./clean.sh --cache          # Remove only tool caches
#   ./clean.sh --venv           # Remove the repo-level Python venv
#   ./clean.sh --backend        # Deep-clean backend: artifacts, caches, and venv
#   ./clean.sh --frontend       # Deep-clean frontend: build output, cache, and node_modules
#   ./clean.sh --all            # Nuclear clean — removes everything (run setup.sh to restore)
#   ./clean.sh --help           # Show usage
# ==============================================================================

set -euo pipefail

# ── Constants ─────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Helpers ───────────────────────────────────────────────────────────────────

info()    { echo -e "${CYAN}ℹ  $*${NC}"; }
ok()      { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
fail()    { echo -e "${RED}❌ $*${NC}"; exit 1; }
section() { echo -e "\n${BOLD}── $* ──${NC}"; }

usage() {
    cat <<EOF
AlphaForge — Cleanup Script

Usage: $(basename "$0") [OPTION]

  (no args)       Remove build artifacts and bytecode (keeps venv + node_modules)
  --cache         Remove only tool caches (__pycache__, .pytest_cache, .ruff_cache, .mypy_cache, .next)
  --venv          Remove the repo-level Python venv (.venv/)
  --backend       Deep-clean backend: artifacts, caches, and venv
  --frontend      Deep-clean frontend: .next, node_modules/.cache, and node_modules
  --all           Nuclear clean — removes everything (run ./setup.sh to restore)
  --help          Show this help message

EOF
    exit 0
}

# ── Clean Functions ───────────────────────────────────────────────────────────

clean_py_caches() {
    info "Removing Python caches..."
    find backend packages -type d -name __pycache__   -exec rm -rf {} + 2>/dev/null || true
    find backend packages -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find backend packages -type d -name .ruff_cache   -exec rm -rf {} + 2>/dev/null || true
    find backend packages -type d -name .mypy_cache   -exec rm -rf {} + 2>/dev/null || true
}

clean_default() {
    section "Cleaning Build Artifacts & Bytecode"
    clean_py_caches
    info "Removing backend dist/egg artifacts..."
    rm -rf backend/dist backend/*.egg-info
    info "Removing frontend build output..."
    rm -rf frontend/.next
    ok "Cleaned"
}

clean_cache() {
    section "Cleaning Tool Caches"
    clean_py_caches
    info "Removing frontend caches..."
    rm -rf frontend/.next frontend/node_modules/.cache
    ok "Caches cleared"
}

clean_venv() {
    section "Removing Python Venv"
    if [[ -d "$VENV_DIR" ]]; then
        rm -rf "$VENV_DIR"
        ok "Venv removed ($VENV_DIR)"
    else
        warn "Venv not found at $VENV_DIR — nothing to remove"
    fi
}

clean_backend() {
    section "Deep-Cleaning Backend"
    clean_py_caches
    info "Removing backend dist/egg artifacts..."
    rm -rf backend/dist backend/*.egg-info
    info "Removing Python venv..."
    rm -rf "$VENV_DIR"
    ok "Backend fully cleaned"
}

clean_frontend() {
    section "Deep-Cleaning Frontend"
    info "Removing .next, node_modules/.cache, and node_modules..."
    rm -rf frontend/.next frontend/node_modules/.cache frontend/node_modules
    ok "Frontend fully cleaned"
}

clean_all() {
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   AlphaForge — Nuclear Clean                 ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    warn "This removes the venv, all node_modules, and all build artifacts."
    read -rp "Are you sure? [y/N] " ans
    if [[ ! "$ans" =~ ^[Yy]$ ]]; then
        info "Aborted."
        exit 0
    fi

    clean_backend
    clean_frontend
    info "Removing root and package node_modules..."
    rm -rf node_modules packages/*/node_modules

    echo ""
    ok "Full clean complete — run './setup.sh' to restore"
    echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────

cd "$REPO_ROOT"

case "${1:-}" in
    --help|-h)  usage ;;
    --cache)    clean_cache ;;
    --venv)     clean_venv ;;
    --backend)  clean_backend ;;
    --frontend) clean_frontend ;;
    --all)      clean_all ;;
    "")         clean_default ;;
    *)          fail "Unknown option: $1 (use --help for usage)" ;;
esac
