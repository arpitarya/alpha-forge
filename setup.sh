#!/usr/bin/env bash
# ==============================================================================
# AlphaForge — Full Repository Setup & Screener Pipeline Runner
# ==============================================================================
# Disclaimer: NOT SEBI registered investment advice. For personal research only.
#
# Usage:
#   ./setup.sh                  # Full repo setup (prereqs + venv + deps + env + dirs)
#   ./setup.sh --prereqs        # Check/install system prerequisites only
#   ./setup.sh --venv           # Create Python venv only
#   ./setup.sh --backend        # Install backend Python dependencies only
#   ./setup.sh --frontend       # Install frontend + workspace Node dependencies only
#   ./setup.sh --screener       # Install screener Python dependencies only
#   ./setup.sh --env            # Create .env files from examples (non-destructive)
#   ./setup.sh --dirs           # Create all required directories
#   ./setup.sh --db             # Setup local PostgreSQL + Redis (macOS Homebrew)
#   ./setup.sh --pipeline       # Run full screener data → train → backtest pipeline
#   ./setup.sh --scan           # Run daily live scan (requires trained models)
#   ./setup.sh --help           # Show usage
# ==============================================================================

set -euo pipefail

# ── Constants ─────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCREENER_DIR="$REPO_ROOT/screener"
VENV_DIR="$REPO_ROOT/.venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

REQUIRED_PYTHON_MAJOR=3
REQUIRED_PYTHON_MINOR=14

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ── Helpers ───────────────────────────────────────────────────────────────────

info()    { echo -e "${CYAN}ℹ  $*${NC}"; }
ok()      { echo -e "${GREEN}✅ $*${NC}"; }
warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; }
fail()    { echo -e "${RED}❌ $*${NC}"; exit 1; }
section() { echo -e "\n${BOLD}── $* ──${NC}"; }

usage() {
    cat <<EOF
AlphaForge — Full Repository Setup & Screener Pipeline

Usage: $(basename "$0") [OPTION]

Setup:
  (no args)       Full setup: prereqs, venv, all deps, env files, directories
  --prereqs       Check/install system prerequisites (pyenv, nvm, pnpm, pdm, brew)
  --venv          Create repo-root Python venv (.venv/) from .python-version
  --backend       Install backend Python dependencies (PDM → .venv)
  --frontend      Install frontend + workspace Node packages (pnpm)
  --screener      Install screener ML dependencies into .venv
  --env           Scaffold .env files from .env.example templates (non-destructive)
  --dirs          Create required directories (logs, screener data, model dirs)
  --db            Setup local PostgreSQL 16 + Redis via Homebrew (macOS only)

Screener Pipeline:
  --pipeline      Run full pipeline: data → features → dataset → train → backtest
  --scan          Run daily live scan (requires trained models)

Misc:
  --help          Show this help message

Prerequisites:
  - macOS (Homebrew) — primary supported platform
  - pyenv (Python 3.14+ pinned in .python-version)
  - nvm (Node.js pinned in .nvmrc)
  - pnpm (workspace package manager)
  - pdm (backend Python package manager)
  - Homebrew (for PostgreSQL, Redis, libomp)

EOF
    exit 0
}

# ── Prerequisite Checks ──────────────────────────────────────────────────────

check_brew() {
    if ! command -v brew &>/dev/null; then
        fail "Homebrew not found. Install from https://brew.sh"
    fi
    ok "Homebrew found"
}

check_pyenv() {
    if ! command -v pyenv &>/dev/null; then
        warn "pyenv not found"
        read -rp "Install pyenv via Homebrew? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            brew install pyenv
            ok "pyenv installed — add 'eval \"\$(pyenv init -)\"' to your shell profile"
        else
            fail "pyenv is required. Install via: brew install pyenv"
        fi
    fi

    local required_ver
    required_ver=$(cat "$REPO_ROOT/.python-version" 2>/dev/null || echo "${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}.2")

    if ! pyenv versions --bare 2>/dev/null | grep -qx "$required_ver"; then
        warn "Python $required_ver not installed in pyenv"
        read -rp "Install Python $required_ver via pyenv? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            pyenv install "$required_ver"
            ok "Python $required_ver installed"
        else
            warn "Skipping Python install. Venv creation may fail."
        fi
    else
        ok "Python $required_ver available (pyenv)"
    fi
}

check_nvm_and_node() {
    local required_node
    required_node=$(cat "$REPO_ROOT/.nvmrc" 2>/dev/null || echo "v24.13.0")

    # Source nvm if available but not loaded
    if ! command -v nvm &>/dev/null; then
        export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
        # shellcheck disable=SC1091
        [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
    fi

    if ! command -v nvm &>/dev/null; then
        warn "nvm not found — install from https://github.com/nvm-sh/nvm"
        # Fall back to checking node directly
        if command -v node &>/dev/null; then
            ok "Node.js found: $(node --version) (nvm not managing it)"
        else
            fail "Neither nvm nor node found. Install nvm first."
        fi
        return
    fi

    # Install the required Node version if missing
    if ! nvm ls "$required_node" &>/dev/null; then
        info "Installing Node.js $required_node via nvm..."
        nvm install "$required_node"
    fi
    nvm use "$required_node" 2>/dev/null || true
    ok "Node.js $(node --version) active (nvm)"
}

check_pnpm() {
    if ! command -v pnpm &>/dev/null; then
        warn "pnpm not found"
        read -rp "Install pnpm via corepack? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            corepack enable
            corepack prepare pnpm@latest --activate
            ok "pnpm installed via corepack"
        else
            fail "pnpm is required. Install via: corepack enable && corepack prepare pnpm@latest --activate"
        fi
    else
        ok "pnpm $(pnpm --version) found"
    fi
}

check_pdm() {
    if ! command -v pdm &>/dev/null; then
        warn "pdm not found"
        read -rp "Install pdm via Homebrew? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            brew install pdm
            ok "pdm installed"
        else
            fail "pdm is required. Install via: brew install pdm"
        fi
    else
        ok "pdm $(pdm --version | head -1) found"
    fi
}

check_macos_deps() {
    if [[ "$(uname)" != "Darwin" ]]; then
        return
    fi

    # LightGBM requires libomp on macOS
    if ! brew list libomp &>/dev/null; then
        warn "libomp not installed — required for LightGBM on macOS"
        read -rp "Install libomp via Homebrew? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            brew install libomp
            ok "libomp installed"
        else
            warn "Skipping libomp install. LightGBM may fail to import."
        fi
    else
        ok "libomp found (required by LightGBM)"
    fi
}

check_all_prereqs() {
    section "Checking Prerequisites"
    check_brew
    check_pyenv
    check_nvm_and_node
    check_pnpm
    check_pdm
    check_macos_deps
}

# ── Python Venv ───────────────────────────────────────────────────────────────

create_venv() {
    section "Python Virtual Environment"

    if [[ -x "$PYTHON" ]]; then
        ok "Venv already exists at $VENV_DIR ($($PYTHON --version))"
        return
    fi

    local required_ver
    required_ver=$(cat "$REPO_ROOT/.python-version" 2>/dev/null || echo "${REQUIRED_PYTHON_MAJOR}.${REQUIRED_PYTHON_MINOR}.2")
    local pyenv_python
    pyenv_python="$(pyenv root)/versions/$required_ver/bin/python"

    if [[ -x "$pyenv_python" ]]; then
        info "Creating venv with pyenv Python $required_ver..."
        "$pyenv_python" -m venv "$VENV_DIR"
    elif command -v "python$required_ver" &>/dev/null; then
        info "Creating venv with python$required_ver..."
        "python$required_ver" -m venv "$VENV_DIR"
    else
        fail "Python $required_ver not found. Run: pyenv install $required_ver"
    fi

    ok "Venv created at $VENV_DIR ($($PYTHON --version))"
}

check_venv() {
    if [[ ! -x "$PYTHON" ]]; then
        fail "Python venv not found at $VENV_DIR. Run './setup.sh --venv' first."
    fi
}

# ── Environment Files ─────────────────────────────────────────────────────────

scaffold_env_files() {
    section "Environment Files"

    local created=0

    # Backend .env from example
    if [[ ! -f "$REPO_ROOT/backend/.env" ]]; then
        if [[ -f "$REPO_ROOT/backend/.env.example" ]]; then
            cp "$REPO_ROOT/backend/.env.example" "$REPO_ROOT/backend/.env"
            ok "Created backend/.env from .env.example"
            ((created++))
        else
            warn "backend/.env.example not found — skipping"
        fi
    else
        ok "backend/.env already exists"
    fi

    # Frontend .env.local from example
    if [[ ! -f "$REPO_ROOT/frontend/.env.local" ]]; then
        if [[ -f "$REPO_ROOT/frontend/.env.example" ]]; then
            cp "$REPO_ROOT/frontend/.env.example" "$REPO_ROOT/frontend/.env.local"
            ok "Created frontend/.env.local from .env.example"
            ((created++))
        else
            warn "frontend/.env.example not found — skipping"
        fi
    else
        ok "frontend/.env.local already exists"
    fi

    if ((created > 0)); then
        warn "Review and update the new .env files with your credentials before running."
    fi
}

# ── Directory Setup ───────────────────────────────────────────────────────────

create_dirs() {
    section "Required Directories"

    local dirs=(
        # Logs
        "$REPO_ROOT/backend/logs"
        "$REPO_ROOT/frontend/logs"
        # Screener data pipeline
        "$SCREENER_DIR/data/raw/ohlcv"
        "$SCREENER_DIR/data/raw/indices"
        "$SCREENER_DIR/data/raw/nse_supplementary"
        "$SCREENER_DIR/features"
        "$SCREENER_DIR/dataset/output"
        "$SCREENER_DIR/models/saved/lightgbm"
        "$SCREENER_DIR/models/saved/xgboost"
        "$SCREENER_DIR/backtest"
        "$SCREENER_DIR/live/picks"
        "$SCREENER_DIR/reports"
        "$SCREENER_DIR/notebooks"
    )

    for d in "${dirs[@]}"; do
        mkdir -p "$d"
    done

    ok "All directories ready"
}

# ── Backend Dependencies ─────────────────────────────────────────────────────

install_backend() {
    section "Backend Dependencies (PDM)"

    check_venv
    info "Installing backend Python dependencies via PDM..."
    cd "$REPO_ROOT/backend" && pdm install
    cd "$REPO_ROOT"
    ok "Backend dependencies installed into $VENV_DIR"
}

# ── Frontend / Workspace Dependencies ─────────────────────────────────────────

install_frontend() {
    section "Frontend & Workspace Dependencies (pnpm)"

    info "Installing workspace Node packages (frontend + packages/*)..."
    cd "$REPO_ROOT" && pnpm install
    ok "Workspace Node packages installed"

    # Build the UI package so the frontend can consume it
    info "Building @alphaforge/solar-orb-ui package..."
    cd "$REPO_ROOT/packages/solar-orb-ui" && pnpm build
    cd "$REPO_ROOT"
    ok "solar-orb-ui built"
}

# ── Screener Dependencies ────────────────────────────────────────────────────

install_screener() {
    section "Screener Dependencies (pip → .venv)"

    check_venv
    info "Installing screener Python dependencies into $VENV_DIR..."
    "$PIP" install --quiet --upgrade pip

    if [[ -f "$SCREENER_DIR/requirements.txt" ]]; then
        "$PIP" install --quiet -r "$SCREENER_DIR/requirements.txt"
        ok "Screener dependencies installed from requirements.txt"
    else
        fail "requirements.txt not found at $SCREENER_DIR/requirements.txt"
    fi

    # Verify critical imports
    info "Verifying critical screener packages..."
    "$PYTHON" -c "
import yfinance, nselib, pandas, pyarrow, ta, numpy, requests
import sklearn, lightgbm, xgboost
print('All packages imported successfully')
" && ok "All critical packages verified" || fail "Some packages failed to import"
}

# ── Database Setup ────────────────────────────────────────────────────────────

setup_db() {
    section "Local Database Setup"

    if [[ "$(uname)" != "Darwin" ]]; then
        warn "Local DB setup currently supports macOS only. Use Docker instead:"
        echo "  docker compose -f infra/docker-compose.yml up postgres redis -d"
        return
    fi

    if [[ -f "$REPO_ROOT/infra/setup-local.sh" ]]; then
        bash "$REPO_ROOT/infra/setup-local.sh"
    else
        fail "infra/setup-local.sh not found"
    fi
}

# ── Full Setup ────────────────────────────────────────────────────────────────

full_setup() {
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   AlphaForge — Full Repository Setup         ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""

    check_all_prereqs
    create_venv
    create_dirs
    scaffold_env_files
    install_backend
    install_frontend
    install_screener

    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   Setup Complete!                            ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    echo "  Next steps:"
    echo ""
    echo "  1. Review & update environment files:"
    echo "     - backend/.env        (DB credentials, API keys)"
    echo "     - frontend/.env.local (API URL, ports)"
    echo ""
    echo "  2. Start local infrastructure (if not running):"
    echo "     just db-local          # PostgreSQL + Redis via Homebrew"
    echo "     # OR: just db-up       # via Docker/OrbStack"
    echo ""
    echo "  3. Run database migrations:"
    echo "     just db-migrate"
    echo ""
    echo "  4. Start development servers:"
    echo "     just dev-local         # Backend + frontend (Procfile)"
    echo "     # OR individually:"
    echo "     just backend           # Backend only"
    echo "     just frontend          # Frontend only"
    echo ""
    echo "  5. Run screener pipeline (optional):"
    echo "     ./setup.sh --pipeline"
    echo ""
}

# ── Screener: Pipeline ───────────────────────────────────────────────────────

run_pipeline() {
    echo ""
    echo "============================================"
    echo "  AlphaForge Screener — Full Pipeline"
    echo "============================================"
    echo ""

    check_venv

    # Phase 1: Data Pipeline
    info "PHASE 1: Data Pipeline"
    echo "────────────────────────────────────────────"

    info "[1.1] Fetching stock universe from NSE..."
    "$PYTHON" -m screener.data.fetch_universe
    ok "Universe fetched"

    info "[1.2] Downloading historical OHLCV data (this may take 10-15 min for full universe)..."
    "$PYTHON" -m screener.data.fetch_ohlcv
    ok "OHLCV data downloaded"

    info "[1.3] Fetching supplementary NSE data (delivery %, bulk/block deals)..."
    "$PYTHON" -m screener.data.fetch_nse_data --nse-only
    ok "NSE supplementary data fetched"

    info "[1.4] Downloading index benchmarks (NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT)..."
    "$PYTHON" -m screener.data.fetch_nse_data --indices-only
    ok "Index benchmarks downloaded"

    echo ""

    # Phase 2: Feature Engineering
    info "PHASE 2: Feature Engineering"
    echo "────────────────────────────────────────────"

    info "[2.x] Building all features (technical, relative strength, fundamental, NSE)..."
    "$PYTHON" -m screener.features.build_features
    ok "Features built"

    echo ""

    # Phase 3: Dataset Construction
    info "PHASE 3: Dataset Construction"
    echo "────────────────────────────────────────────"

    info "[3.x] Building ML-ready dataset (features + labels)..."
    "$PYTHON" -m screener.dataset.build_dataset
    ok "Dataset built"

    echo ""

    # Phase 4: Model Training
    info "PHASE 4: Model Training"
    echo "────────────────────────────────────────────"

    info "[4.1] Running baseline rules strategies..."
    "$PYTHON" -m screener.models.baseline_rules --strategy all
    ok "Baseline evaluation complete"

    info "[4.2] Training LightGBM classifier (walk-forward CV)..."
    "$PYTHON" -m screener.models.train_lightgbm
    ok "LightGBM trained and saved"

    info "[4.3] Training XGBoost classifier (walk-forward CV)..."
    "$PYTHON" -m screener.models.train_xgboost
    ok "XGBoost trained and saved"

    info "[4.5] Generating feature importance report..."
    "$PYTHON" -m screener.models.feature_importance --save-report
    ok "Feature importance report saved"

    echo ""

    # Phase 5: Backtesting
    info "PHASE 5: Backtesting"
    echo "────────────────────────────────────────────"

    info "[5.x] Running backtest engine across all strategies..."
    "$PYTHON" -m screener.backtest.engine
    ok "Backtest engine complete"

    info "[5.4] Generating comparison report..."
    "$PYTHON" -m screener.backtest.report
    ok "Backtest report saved to screener/reports/"

    echo ""
    echo "============================================"
    ok "Full pipeline complete!"
    echo "============================================"
    echo ""
    echo "  Reports:  screener/reports/backtest_report.txt"
    echo "  Models:   screener/models/saved/{lightgbm,xgboost}/"
    echo ""
    echo "  Run daily scan:  ./setup.sh --scan"
    echo ""
}

# ── Screener: Daily Scan ─────────────────────────────────────────────────────

check_trained_models() {
    local lgb_model="$SCREENER_DIR/models/saved/lightgbm/model.txt"
    local xgb_model="$SCREENER_DIR/models/saved/xgboost/model.json"
    if [[ ! -f "$lgb_model" ]] && [[ ! -f "$xgb_model" ]]; then
        fail "No trained models found. Run '--pipeline' first to train models."
    fi
    [[ -f "$lgb_model" ]] && ok "LightGBM model found"
    [[ -f "$xgb_model" ]] && ok "XGBoost model found"
}

run_scan() {
    echo ""
    echo "============================================"
    echo "  AlphaForge Screener — Daily Scan"
    echo "============================================"
    echo ""

    check_venv
    check_trained_models

    info "Updating OHLCV data (incremental)..."
    "$PYTHON" -m screener.data.fetch_ohlcv --incremental
    ok "OHLCV data updated"

    info "Running daily scan with LightGBM..."
    "$PYTHON" -m screener.live.scan --model lightgbm --top-n 20
    ok "LightGBM scan complete"

    info "Running daily scan with XGBoost..."
    "$PYTHON" -m screener.live.scan --model xgboost --top-n 20
    ok "XGBoost scan complete"

    info "Generating signal explanations..."
    "$PYTHON" -m screener.live.explain --model lightgbm --top-n 10
    ok "Explanations generated"

    info "Checking model drift..."
    "$PYTHON" -m screener.live.retrain drift --model all
    ok "Drift check complete"

    echo ""
    ok "Daily scan complete! Picks saved to screener/live/picks/"
    echo ""
}

# ── Main ──────────────────────────────────────────────────────────────────────

cd "$REPO_ROOT"

case "${1:-}" in
    --help|-h)      usage ;;
    --prereqs)      check_all_prereqs ;;
    --venv)         create_venv ;;
    --backend)      install_backend ;;
    --frontend)     install_frontend ;;
    --screener)     install_screener ;;
    --env)          scaffold_env_files ;;
    --dirs)         create_dirs ;;
    --db)           setup_db ;;
    --pipeline)     run_pipeline ;;
    --scan)         run_scan ;;
    "")             full_setup ;;
    *)              fail "Unknown option: $1 (use --help for usage)" ;;
esac
