# AlphaForge

**AI-Powered Financial Analysis & Trading Terminal for Indian Markets**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

AlphaForge is an open-source, institutional-grade financial analysis and trading platform — like a Bloomberg Terminal built for Indian retail & professional investors, supercharged with AI.

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge

# Option 1: Docker (recommended)
cp backend/.env.example backend/.env   # edit with your keys
docker compose up --build

# Option 2: Local development
make backend-install    # Python deps
make frontend-install   # Node deps
make db-up              # Start PostgreSQL & Redis
make backend            # Start API at :8000
make frontend           # Start UI at :3000
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
├── backend/                 # Python/FastAPI API server
│   ├── app/
│   │   ├── core/            # Config, DB, security
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic & integrations
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend tests
│   └── pyproject.toml
├── frontend/                # Next.js / React / TypeScript UI
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   └── lib/             # API client, stores, utils
│   └── package.json
├── docs/                    # Project documentation
├── docker-compose.yml       # Full-stack orchestration
├── Makefile                 # Dev commands
└── LICENSE
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Backend API | Python 3.12 + FastAPI | Async, fast, great ML ecosystem |
| Frontend | Next.js 15 + React 19 + TypeScript | Modern, fast, SSR support |
| Database | PostgreSQL 16 | Reliable, battle-tested |
| Cache / Pub-Sub | Redis 7 | Real-time data, WebSocket backing |
| AI / LLM | OpenAI + LangChain | Conversational AI, RAG |
| Charts | Lightweight Charts (TradingView) | Professional-grade charts |
| Broker API | Zerodha Kite Connect | Most popular Indian broker API |
| Task Queue | Celery | Background jobs (screeners, alerts) |
| Styling | Tailwind CSS v4 | Utility-first, terminal aesthetic |
| Containers | Docker Compose | One-command dev environment |

---

## License

MIT — see [LICENSE](LICENSE).
