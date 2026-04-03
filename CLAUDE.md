# CLAUDE.md — Context for Claude Code

## Project

**AlphaForge** — AI-powered financial analysis & trading terminal for Indian markets.
Open-source Bloomberg Terminal alternative. MIT licensed.

## Repository Structure

```
alpha-forge/
├── backend/          Python 3.12 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt security
│   ├── app/models/   SQLAlchemy ORM: User, Holding, Order, Watchlist
│   ├── app/routes/   FastAPI routers: health, auth, market, portfolio, ai, trade
│   ├── app/services/ Business logic: broker_base (ABC), broker_zerodha, ai_service, market_data
│   ├── alembic/      Database migrations
│   └── tests/        Pytest suite
├── frontend/         Next.js 15 (App Router) + React 19 + TypeScript + Tailwind v4
│   ├── src/app/      Pages and layouts
│   ├── src/components/  UI components (layout, dashboard, ai)
│   └── src/lib/      API client (axios), Zustand store
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── docs/             WHY.md, WHAT.md, HOW.md, GETTING_STARTED.md
└── design/           Design system & Figma tokens
```

## Tech Decisions

| Area | Choice | Notes |
|------|--------|-------|
| Python pkg mgr | PDM + uv | `pdm install` uses uv for resolution/install |
| Node pkg mgr | pnpm | Lockfile: `pnpm-lock.yaml` |
| DB | PostgreSQL 16 | Async via asyncpg + SQLAlchemy |
| Cache | Redis 7 | Quotes cache, pub/sub, Celery broker |
| AI | OpenAI + LangChain | RAG with market data context |
| Brokers | Abstract BaseBroker interface | Zerodha first, then Angel One, Upstox |
| Local infra | brew services (Postgres, Redis) | Containers optional via OrbStack |
| CI infra | devcontainer.json | GitHub Codespaces compatible |

## Coding Conventions

### Python
- Async everywhere (routes, services, DB queries)
- Absolute imports: `from app.core.config import settings`
- Type hints on all function signatures
- Ruff for lint+format (line-length=100)
- Pydantic v2 for request/response models
- SQLAlchemy 2.0 `mapped_column` style

### TypeScript
- Strict mode, no `any` unless justified
- Functional components only
- Zustand for state (no Redux, no Context for global state)
- Axios client in `src/lib/api.ts` — all API calls go through it
- Tailwind utility classes; custom CSS vars for dark terminal theme

## Key Files
- `backend/app/main.py` — FastAPI app factory
- `backend/app/core/config.py` — All environment variables
- `backend/app/services/broker_base.py` — Abstract broker interface (implement this for new brokers)
- `frontend/src/app/page.tsx` — Main dashboard
- `frontend/src/lib/api.ts` — Backend API client
- `frontend/src/app/globals.css` — Theme variables

## Commands

```bash
# Backend
cd backend && pdm install           # Install deps
cd backend && pdm run dev           # Start server (uvicorn --reload)
cd backend && pdm run pytest -v     # Tests
cd backend && pdm run ruff check .  # Lint

# Frontend
cd frontend && pnpm install         # Install deps
cd frontend && pnpm dev             # Dev server
cd frontend && pnpm lint            # Lint
cd frontend && pnpm type-check      # TypeScript check

# Infrastructure
brew services start postgresql@16 && brew services start redis  # macOS native
# OR: docker compose -f infra/docker-compose.yml up -d          # via OrbStack

# Migrations
cd backend && pdm run alembic upgrade head
cd backend && pdm run alembic revision --autogenerate -m "description"
```

## Guardrails
- Never commit `.env` files or API keys
- All AI outputs must include financial disclaimer
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only
- No guaranteed return claims anywhere in code or UI
