# Getting Started — Developer Setup

## Prerequisites

| Tool | Version | Install | Notes |
|------|---------|---------|-------|
| pyenv | Latest | `brew install pyenv` | Manages Python versions; reads `.python-version` |
| Python | 3.14+ | `pyenv install 3.14.2` | Pinned in `.python-version` |
| PDM | Latest | `brew install pdm` | Installs into repo-root `.venv/` (see `backend/pdm.toml`) |
| uv | Latest | `brew install uv` | Fast resolver/installer for PDM |
| nvm | Latest | [nvm-sh/nvm](https://github.com/nvm-sh/nvm) | Manages Node versions; reads `.nvmrc` |
| Node.js | 22+ | `nvm install` | Pinned in `.nvmrc` |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest --activate` | Config in `.npmrc` |
| Git | Latest | `brew install git` | — |

**Optional (for container workflow):**

| Tool | Install | Notes |
|------|---------|-------|
| OrbStack | [orbstack.dev](https://orbstack.dev) | Lightweight Docker alternative for macOS (~6x less RAM than Docker Desktop) |
| Docker Desktop | [docker.com](https://www.docker.com/products/docker-desktop) | Heavier but more established |

> **For MacBook Air M4 (16GB RAM):** We recommend the **native local setup** (Option 1 below). It uses Homebrew to run PostgreSQL and Redis natively with zero container overhead. If you need containers, use **OrbStack** instead of Docker Desktop — it's purpose-built for Apple Silicon and uses a fraction of the memory.

---

## Option 1: Native Local Development (Recommended for macOS)

The fastest, lightest setup — no Docker at all:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge

# 2. Full automated setup (prereqs check, venv, deps, env files, dirs)
./setup.sh
# This checks pyenv/nvm/pnpm/pdm, creates .venv, installs all deps,
# scaffolds .env files, and creates required directories.

# 3. Setup PostgreSQL & Redis via Homebrew
./setup.sh --db
# OR: just db-local

# 4. Review & update environment files
# Edit backend/.env and frontend/.env.local with your credentials

# 5. Run database migrations
just db-migrate

# 6. Start development servers
just dev-local              # Backend + frontend via Procfile
```

**Or step-by-step if you prefer granular control:**
```bash
./setup.sh --prereqs        # Check/install system tools
./setup.sh --venv           # Create .venv from .python-version
./setup.sh --backend        # Install backend deps (PDM)
./setup.sh --frontend       # Install frontend + workspace deps (pnpm)
./setup.sh --screener       # Install screener ML deps (pip)
./setup.sh --env            # Scaffold .env files from templates
./setup.sh --dirs           # Create log/data/model directories
./setup.sh --db             # Setup local PostgreSQL + Redis
```

**Start everything at once** with a process manager:
```bash
brew install overmind       # or: pip install honcho
just dev-local              # Starts backend + frontend from Procfile
```

---

## Option 2: Containers (OrbStack or Docker)

If you prefer containers, or are on Linux/Windows:

```bash
# 1. Install OrbStack (macOS) or Docker Desktop
# OrbStack: brew install orbstack  (recommended for Apple Silicon)
# Docker:   brew install --cask docker

# 2. Clone and configure
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge
cp backend/.env.example backend/.env

# 3. Start everything
docker compose -f infra/docker-compose.yml up --build

# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/docs
# Frontend:    http://localhost:3000
```

---

## Option 3: GitHub Codespaces

This repo includes a `.devcontainer/devcontainer.json` for instant cloud development:

1. Go to the GitHub repo → Click **Code** → **Codespaces** → **Create codespace**
2. Wait for the container to build (installs pdm + pnpm + all deps)
3. Backend and frontend are ready to start:
   ```bash
   cd backend && pdm run dev      # Terminal 1
   cd frontend && pnpm dev        # Terminal 2
   ```
4. Codespaces auto-forwards ports 8000 and 3000

---

## Configuration

### Required Environment Variables

All ports are defined in [`.env.port`](../.env.port) at the repo root. Credentials live in `.env.cred` (see `.env.cred.example`). Copy the example files:

```bash
cp .env.example .env                 # Root env (used by docker-compose)
cp .env.cred.example .env.cred       # Credentials (API keys, passwords, secrets)
cp backend/.env.example backend/.env  # Backend
cp frontend/.env.example frontend/.env.local  # Frontend (Next.js uses .env.local)
```

The only **required** variables for basic operation:

```bash
SECRET_KEY=<a-random-string-for-JWT>
DATABASE_URL=postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge
REDIS_URL=redis://localhost:6379/0
```

### Optional — AI Features

```bash
OPENAI_API_KEY=sk-...       # Required for AI chat and analysis
OPENAI_MODEL=gpt-4o         # Or gpt-4o-mini for cheaper testing
```

### Optional — Broker Integration

```bash
# Zerodha Kite (get from https://developers.kite.trade)
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
```

---

## Common Commands

```bash
# ── Setup ────────────────────────────────────────
./setup.sh                 # Full repo setup (prereqs, venv, all deps, env, dirs)
./setup.sh --prereqs       # Check/install system prerequisites
./setup.sh --venv          # Create Python venv only
./setup.sh --backend       # Install backend deps only
./setup.sh --frontend      # Install frontend deps only
./setup.sh --screener      # Install screener ML deps only
./setup.sh --env           # Scaffold .env files from examples
./setup.sh --dirs          # Create required directories
./setup.sh --db            # Setup local PostgreSQL + Redis (macOS)
./setup.sh --help          # Show all setup.sh options

# ── Development ──────────────────────────────────
just help                  # Show all available Makefile commands
just dev-local             # Start backend + frontend via Procfile
just dev-docker            # Start everything with Docker/OrbStack
just backend               # Run backend locally (pdm run dev)
just frontend              # Run frontend locally (pnpm dev)

# ── Testing & Quality ────────────────────────────
just test                  # Run all tests
just lint                  # Lint backend + frontend
just format                # Auto-format backend code

# ── Database ─────────────────────────────────────
just db-local              # Setup PostgreSQL + Redis via Homebrew
just db-up                 # Start PostgreSQL + Redis via Docker
just db-migrate            # Apply pending migrations
just db-revision msg="description"  # Create new migration

# ── Screener Pipeline ────────────────────────────
./setup.sh --pipeline      # Run full data → train → backtest pipeline
./setup.sh --scan          # Run daily live scan
just screener-pipeline     # Same as above, via Makefile
just screener-scan         # Same as above, via Makefile

# ── Misc ─────────────────────────────────────────
just setup-mcp             # Install Playwright MCP for Copilot browser integration
```

---

## Project Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   └── security.py      # JWT + password hashing
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── portfolio.py     # Holding, Order, Watchlist models
│   ├── routes/
│   │   ├── __init__.py      # Central router registry
│   │   ├── health.py        # GET /health
│   │   ├── auth.py          # POST /auth/register, /auth/login
│   │   ├── market.py        # GET /market/quote, /indices, /history
│   │   ├── portfolio.py     # GET /portfolio/summary, /positions
│   │   ├── ai.py            # POST /ai/chat, /ai/analyze
│   │   └── trade.py         # POST /trade/order
│   └── services/
│       ├── broker_base.py   # Abstract broker interface
│       ├── broker_zerodha.py# Zerodha Kite implementation
│       ├── ai_service.py    # LLM orchestration
│       └── market_data.py   # Market data fetcher
├── alembic/                 # Database migrations
├── tests/                   # Pytest test suite
├── Dockerfile
├── pyproject.toml           # PDM config (uses uv resolver)
└── .env.example

packages/
└── solar-orb-ui/            # @alphaforge/solar-orb-ui publishable package
    ├── src/
    │   ├── index.ts         # Barrel export (components + tokens)
    │   ├── components/      # Button, Input, Card, Badge, Icon, Text
    │   ├── tokens/          # Design tokens (TypeScript + JSON)
    │   │   ├── index.ts     # TS token constants
    │   │   └── tokens.json  # Machine-readable token definitions
    │   └── styles/          # fonts.css, theme.css, base.css
    ├── tsup.config.ts       # Build config → ESM + CJS + DTS
    └── package.json

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout (dark theme, Space Grotesk font)
│   │   ├── page.tsx         # Terminal landing page (Solar Terminal dashboard)
│   │   └── globals.css      # Global styles, design tokens, Solar Terminal theme
│   ├── components/
│   │   ├── layout/          # Header (floating nav), Sidebar (expandable)
│   │   ├── terminal/        # Terminal landing page components
│   │   │   ├── index.ts         # Barrel export for all terminal components
│   │   │   ├── SolarOrb.tsx     # Central glowing orb hero element
│   │   │   ├── AlphaBrief.tsx   # Market sentiment & risk alert card
│   │   │   ├── TerminalWatchlist.tsx # Floating watchlist shard
│   │   │   ├── PortfolioCards.tsx   # Net Worth & Allocation cards
│   │   │   ├── RiskAnalysis.tsx     # Risk analysis bar chart shard
│   │   │   └── VoiceFooter.tsx      # Voice/text input footer bar
│   │   ├── dashboard/       # MarketOverview, Watchlist (data views)
│   │   └── ai/              # AIChat component
│   └── lib/
│       ├── api.ts           # Axios API client
│       └── store.ts         # Zustand state management
├── package.json             # pnpm managed
├── tsconfig.json
├── next.config.mjs
└── Dockerfile

infra/
├── docker-compose.yml       # Container orchestration (optional)
└── setup-local.sh           # Native macOS setup (Homebrew)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` |
| Port 3000 already in use | `lsof -ti:3000 \| xargs kill` |
| `pdm install` fails | Ensure pdm + uv are installed: `brew install pdm uv` |
| `pnpm` not found | Enable corepack: `corepack enable && corepack prepare pnpm@latest --activate` |
| PostgreSQL won't start (brew) | `brew services restart postgresql@16` |
| `ta-lib` install fails | Install system lib: `brew install ta-lib` |
| Frontend can't reach backend | Check CORS config in `.env` and Next.js rewrite proxy |
| Alembic migration fails | Ensure DB is running: `brew services list` or `just db-up` |
| Docker too heavy on macOS | Use native setup: `bash infra/setup-local.sh` or install OrbStack |

---

## Copilot + Browser Integration (Playwright MCP)

Copilot can connect to Chrome to review mockups, screenshot live pages, and iterate on UI:

```bash
just setup-mcp          # Install Playwright Chromium + configure MCP
```

This installs the Playwright Chromium browser and configures the MCP server in `.vscode/settings.json`. After installation:

1. **Restart VS Code** to activate the MCP server
2. Copilot can now open URLs, take screenshots, click elements, and inspect your running frontend
3. Use it to compare mockups (e.g. `design/terminal aka landing page/code.html`) against the live dev server

The MCP configuration lives in [`.vscode/settings.json`](../.vscode/settings.json):
```json
{
  "mcp": {
    "servers": {
      "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
      }
    }
  }
}
```

---

## Next Steps

Once the base setup is running:

1. **Explore the API** at http://localhost:8000/docs
2. **Try the AI chat** (once you add an OpenAI key)
3. **Connect a broker** (get Zerodha Kite API key from developers.kite.trade)
4. **Set up Copilot browser integration** — `just setup-mcp` (see above)
5. **Check the roadmap** in [WHAT.md](WHAT.md) for upcoming features
6. **Open in Codespaces** for zero-setup cloud development
7. **Contribute** — pick an issue, create a PR!
