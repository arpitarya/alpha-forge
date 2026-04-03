# AlphaForge — Project Guidelines

## What This Is

AI-powered financial analysis & trading terminal for Indian markets (NSE/BSE).
Monorepo: Python/FastAPI backend + Next.js/TypeScript frontend.

## Architecture

- **Backend** (`backend/`): Python 3.12, FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis, Celery
- **Frontend** (`frontend/`): Next.js 15 (App Router), React 19, TypeScript strict, Tailwind CSS v4
- **AI Layer**: OpenAI + LangChain for market analysis, RAG, conversational chat
- **Broker Integration**: Abstract `BaseBroker` interface in `backend/app/services/broker_base.py` — all brokers implement this

## Code Style

### Python (backend/)
- **Package manager**: PDM with uv as resolver/installer (`pdm install`, NOT pip)
- **Formatter/Linter**: ruff (line-length=100, target py311)
- **Type hints**: Required on all function signatures
- **Async**: Use `async def` for all route handlers and service methods
- **Models**: SQLAlchemy 2.0 `mapped_column` style (see `backend/app/models/`)
- **Config**: Pydantic `BaseSettings` loaded from `.env` (see `backend/app/core/config.py`)
- **Imports**: Use absolute imports from `app.` (e.g., `from app.core.config import settings`)

### TypeScript (frontend/)
- **Package manager**: pnpm (NOT npm or yarn)
- **Strict mode**: enabled in tsconfig.json
- **Components**: Functional components only, no class components
- **State management**: Zustand stores in `frontend/src/lib/store.ts`
- **API calls**: Use the typed API client in `frontend/src/lib/api.ts` (axios-based)
- **Styling**: Tailwind utility classes; CSS variables for the AlphaForge dark theme (defined in `globals.css`)
- **File naming**: PascalCase for components (`MarketOverview.tsx`), camelCase for utilities (`api.ts`)

## Build & Run

```bash
# Infrastructure (PostgreSQL + Redis) — choose one:
brew services start postgresql@16 && brew services start redis    # Native macOS
# OR
docker compose -f infra/docker-compose.yml up -d                  # Container (OrbStack recommended over Docker Desktop)

# Backend
cd backend && pdm install && pdm run dev

# Frontend
cd frontend && pnpm install && pnpm dev

# All at once
make dev-local
```

## Conventions

- **API routes** live in `backend/app/routes/` — one file per domain (market, trade, ai, etc.)
- **Services** live in `backend/app/services/` — business logic, never in route handlers
- **New broker?** Implement `BaseBroker` in `backend/app/services/broker_{name}.py`
- **Database migrations**: `cd backend && pdm run alembic revision --autogenerate -m "description"`
- **Environment variables**: Add to `backend/.env.example` with comments — never commit `.env`
- **AI outputs always include disclaimer**: "Not SEBI registered investment advice"
- All financial amounts use `float` for now (will migrate to `Decimal` before production)

## Testing

- Backend: `cd backend && pdm run pytest -v`
- Frontend: `cd frontend && pnpm lint && pnpm type-check`

## Documentation

Detailed docs in `docs/`: WHY.md (vision), WHAT.md (features), HOW.md (architecture), GETTING_STARTED.md (setup).
