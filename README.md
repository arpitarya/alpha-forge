# AlphaForge

<p align="center">
  <img src="logo.png" alt="AlphaForge Logo" width="400" />
</p>

**Personal AI-Powered Portfolio Management & Investment Terminal for Indian Markets**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AlphaForge is an open-source, AI-powered personal portfolio management and investment tool for Indian markets (NSE/BSE). Built for managing your own investments — combining market data, analysis, and trade execution in a single terminal interface.

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge

# Option 1: Native macOS (recommended for M-series Macs — zero Docker overhead)
bash infra/setup-local.sh           # Install & start PostgreSQL + Redis via Homebrew
cp backend/.env.example backend/.env
cd backend && pdm install && pdm run dev    # API at :8000
cd frontend && pnpm install && pnpm dev     # UI at :3000

# Option 2: All-in-one with process manager
make db-local                       # Setup PostgreSQL + Redis via Homebrew
make backend-install && make frontend-install
make dev-local                      # Starts backend + frontend via Procfile

# Option 3: Containers (OrbStack recommended over Docker Desktop)
cp backend/.env.example backend/.env
docker compose -f infra/docker-compose.yml up --build
```

**Backend API docs:** http://localhost:8000/docs  
**Frontend:** http://localhost:3000

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/WHY.md](docs/WHY.md) | Why AlphaForge exists — the problem & vision |
| [docs/WHAT.md](docs/WHAT.md) | What AlphaForge is — features, scope, roadmap |
| [docs/HOW.md](docs/HOW.md) | How it works — architecture, tech stack, design |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Setup guide for developers |

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
| AI / LLM | OpenAI + LangChain | Conversational AI, RAG |
| Charts | Lightweight Charts (TradingView) | Professional-grade charts |
| Broker API | Zerodha Kite Connect | Most popular Indian broker API |
| Task Queue | Celery | Background jobs (screeners, alerts) |
| Styling | Tailwind CSS v4 | Utility-first, terminal aesthetic |
| Local Infra | Homebrew (native) or OrbStack | Lightweight, M-series optimized |

---

## License

MIT — see [LICENSE](LICENSE).
