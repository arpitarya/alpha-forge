# AlphaForge

<p align="center">
  <img src="logo.png" alt="AlphaForge Logo" width="400" />
</p>

**Personal AI-powered Portfolio Management and Investment Terminal for Indian Markets**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AlphaForge is an open-source personal investment terminal for Indian markets (NSE/BSE). It combines a FastAPI backend, a Next.js frontend, an ML screener pipeline, and a multi-provider LLM gateway.

This project is built for personal use and research.

Not SEBI registered investment advice.

---

## What Is New

- Added `llm-gateway/` package with 5-provider routing: Gemini, Groq, HuggingFace, OpenRouter, Ollama
- Added backend `/llm` endpoints for completion, screener analysis, explanation, provider health, and benchmark
- Added frontend typed LLM API integration and React Query hooks
- Expanded screener implementation across data, features, dataset, models, and backtesting phases
- Standardized setup with `./setup.sh` full and granular workflows
- Added workspace packages:
  - `packages/logger-py` (`alphaforge-logger`)
  - `packages/logger-node` (`@alphaforge/logger`)
  - `packages/solar-orb-ui` (`@alphaforge/solar-orb-ui`)

---

## Monorepo Overview

| Module | Path | Purpose |
|--------|------|---------|
| Backend | `backend/` | FastAPI API, auth, market, portfolio, broker integration, LLM routes |
| Frontend | `frontend/` | Next.js terminal UI, dashboard, AI surfaces |
| UI Library | `packages/solar-orb-ui/` | Shared design tokens and UI components |
| Logging Packages | `packages/logger-py/`, `packages/logger-node/` | Shared logging for Python and Node |
| LLM Gateway | `llm-gateway/` | Provider routing, cost guardrails, CLI, benchmarks |
| Screener | `screener/` | Data pipeline, feature engineering, model training, backtests |
| Infra | `infra/` | Docker Compose and local setup scripts |

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge

# Recommended: full setup
./setup.sh

# Start PostgreSQL + Redis locally (macOS)
./setup.sh --db

# Apply DB migrations
just db-migrate

# Start backend + frontend
just dev-local
```

Frontend: http://localhost:3000  
Backend API: http://localhost:8000  
OpenAPI docs: http://localhost:8000/docs

### Alternate Setup Modes

```bash
# Granular setup
./setup.sh --prereqs
./setup.sh --venv
./setup.sh --backend
./setup.sh --frontend
./setup.sh --screener
./setup.sh --env
./setup.sh --dirs

# Containers (OrbStack or Docker)
docker compose -f infra/docker-compose.yml up --build
```

---

## Common Commands

```bash
# Development
just dev-local
just backend
just frontend

# Quality
just test
just lint
just format

# Screener
./setup.sh --pipeline
./setup.sh --scan
just screener-pipeline
just screener-scan

# LLM Gateway
just llm-gateway-install
just llm-providers
just llm-benchmark
python -m alphaforge_llm_gateway chat

# Copilot browser integration
just setup-mcp
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/WHY.md](docs/WHY.md) | Why AlphaForge exists — the problem & vision |
| [docs/WHAT.md](docs/WHAT.md) | What AlphaForge is — features, scope, roadmap |
| [docs/HOW.md](docs/HOW.md) | How it works — architecture, tech stack, design |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Setup guide for developers |
| [screener/PLAN.md](screener/PLAN.md) | Screener planning phases |
| [screener/implement.txt](screener/implement.txt) | Screener implementation log |
| [llm-gateway/PLAN.md](llm-gateway/PLAN.md) | LLM Gateway planning phases |
| [llm-gateway/implement.txt](llm-gateway/implement.txt) | LLM Gateway implementation log |

---

## Project Structure

```
alpha-forge/
├── backend/                 # Python/FastAPI API server (PDM + uv)
│   ├── app/
│   │   ├── core/            # Config, DB, security
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic & integrations
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   └── pyproject.toml
├── frontend/                # Next.js / React / TypeScript UI (pnpm)
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   └── lib/             # API client, stores, utils
│   └── package.json
├── packages/                # Workspace packages
│   ├── logger-py/           # alphaforge-logger
│   ├── logger-node/         # @alphaforge/logger
│   └── solar-orb-ui/        # @alphaforge/solar-orb-ui
├── llm-gateway/             # Multi-provider LLM package + CLI
├── screener/                # ML screener pipeline and backtests
├── infra/                   # Infrastructure configs
│   ├── docker-compose.yml   # Container orchestration (optional)
│   └── setup-local.sh       # Native macOS setup (Homebrew)
├── design/                  # Design system & Gemini Stitch tokens
├── .devcontainer/           # GitHub Codespaces config
├── .github/                 # Copilot instructions
├── CLAUDE.md                # Claude Code context
├── docs/                    # Project documentation
├── Procfile                 # Process manager (overmind/honcho)
├── Makefile                 # Dev commands
└── LICENSE
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | Python 3.14 + FastAPI | Async, fast, great ML ecosystem |
| Python Tooling | PDM + uv | Fast resolver, lockfile, reproducible |
| Frontend | Next.js 15 + React 19 + TypeScript | Modern, fast, SSR support |
| Node Tooling | pnpm | Fast, disk-efficient, strict |
| Database | PostgreSQL 16 | Reliable, battle-tested |
| Cache / Pub-Sub | Redis 7 | Real-time data, WebSocket backing |
| AI / LLM | OpenAI + LangChain + `alphaforge-llm-gateway` | Conversational AI, RAG, provider routing |
| Charts | Lightweight Charts (TradingView) | Professional-grade charts |
| Broker API | Zerodha Kite Connect | Most popular Indian broker API |
| Task Queue | Celery | Background jobs (screeners, alerts) |
| Styling | Tailwind CSS v4 | Utility-first, terminal aesthetic |
| Local Infra | Homebrew (native) or OrbStack | Lightweight, M-series optimized |

---

## License

MIT — see [LICENSE](LICENSE).
