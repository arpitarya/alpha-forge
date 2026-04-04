# Getting Started — Developer Setup

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | `brew install python@3.12` |
| PDM | Latest | `brew install pdm` or `pip install pdm` |
| uv | Latest | `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 22+ | `brew install node` |
| pnpm | 9+ | `corepack enable && corepack prepare pnpm@latest --activate` |
| Git | Latest | `brew install git` |

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

# 2. Setup PostgreSQL & Redis via Homebrew
bash infra/setup-local.sh
# This installs & starts PostgreSQL 16 + Redis 7 and creates the alphaforge database

# 3. Backend setup
cd backend
cp .env.example .env       # Edit with your keys
pdm install                # Installs Python deps using uv resolver
pdm run migrate            # Apply database schema
pdm run dev                # Start API at http://localhost:8000

# 4. Frontend setup (in another terminal)
cd frontend
pnpm install               # Install Node deps
pnpm dev                   # Start UI at http://localhost:3000
```

**Or start everything at once** with a process manager:
```bash
brew install overmind       # or: pip install honcho
make dev-local              # Starts backend + frontend from Procfile
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
make help              # Show all available commands
make dev-local         # Start backend + frontend via Procfile
make dev-docker        # Start everything with Docker/OrbStack
make backend           # Run backend locally (pdm run dev)
make frontend          # Run frontend locally (pnpm dev)
make test              # Run all tests
make lint              # Lint backend + frontend
make format            # Auto-format backend code
make db-local          # Setup PostgreSQL + Redis via Homebrew
make db-up             # Start PostgreSQL + Redis via Docker
make db-migrate        # Apply pending migrations
make db-revision msg="description"  # Create new migration
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
| Alembic migration fails | Ensure DB is running: `brew services list` or `make db-up` |
| Docker too heavy on macOS | Use native setup: `bash infra/setup-local.sh` or install OrbStack |

---

## Next Steps

Once the base setup is running:

1. **Explore the API** at http://localhost:8000/docs
2. **Try the AI chat** (once you add an OpenAI key)
3. **Connect a broker** (get Zerodha Kite API key from developers.kite.trade)
4. **Check the roadmap** in [WHAT.md](WHAT.md) for upcoming features
5. **Open in Codespaces** for zero-setup cloud development
6. **Contribute** — pick an issue, create a PR!
