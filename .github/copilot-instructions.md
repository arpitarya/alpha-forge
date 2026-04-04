# AlphaForge — Project Guidelines

## What This Is

Personal AI-powered portfolio management & investment terminal for Indian markets (NSE/BSE). Built for personal use — not a SaaS product.
Monorepo (pnpm workspaces): Python/FastAPI backend + Next.js/TypeScript frontend + `@alphaforge/solar-orb-ui` design system package.

## Architecture

- **Backend** (`backend/`): Python 3.14, FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis, Celery
- **Frontend** (`frontend/`): Next.js 15 (App Router), React 19, TypeScript strict, Tailwind CSS v4, TanStack React Query v5
- **UI Package** (`packages/solar-orb-ui/`): Publishable component library (Button, Input, Card, Badge, Icon, Text) + design tokens + fonts. Built with tsup → ESM + CJS + DTS
- **AI Layer**: OpenAI + LangChain for market analysis, RAG, conversational chat
- **Broker Integration**: Abstract `BaseBroker` interface in `backend/app/services/broker_base.py` — all brokers implement this

## Code Style

### Python (backend/)
- **Package manager**: PDM with uv as resolver/installer (`pdm install`, NOT pip). Uses repo-root venv (`.venv/`) configured via `backend/pdm.toml`
- **Python version**: Pinned via `.python-version` (pyenv) — currently 3.14.2
- **Formatter/Linter**: ruff (line-length=100, target py314)
- **Type hints**: Required on all function signatures
- **Async**: Use `async def` for all route handlers and service methods
- **Models**: SQLAlchemy 2.0 `mapped_column` style (see `backend/app/models/`)
- **Config**: Pydantic `BaseSettings` loaded from `.env` (see `backend/app/core/config.py`)
- **Imports**: Use absolute imports from `app.` (e.g., `from app.core.config import settings`)

### TypeScript (frontend/)
- **Package manager**: pnpm (NOT npm or yarn). Config in `.npmrc` (exact versions, engine-strict)
- **Node version**: Pinned via `.nvmrc` (nvm)
- **Strict mode**: enabled in tsconfig.json
- **Components**: Functional components only, no class components
- **State management**: Zustand stores in `frontend/src/lib/store.ts`
- **API calls**: Use the typed API client in `frontend/src/lib/api.ts` (axios-based)
- **Styling**: Tailwind utility classes; CSS variables for the Solar Terminal dark theme (defined in `globals.css`). Font: Space Grotesk. Uses Material Symbols Outlined for icons.
- **UI components**: Import from `@alphaforge/solar-orb-ui` or via re-export at `@/components/solar-orb`
- **Linting**: Biome v2 for formatting + linting; ESLint v9 flat config for Next.js rules
- **Data fetching**: TanStack React Query v5 — typed hooks in `frontend/src/lib/queries.ts`
- **File naming**: PascalCase for components (`MarketOverview.tsx`), camelCase for utilities (`api.ts`)
- **Terminal components**: Landing page components live in `frontend/src/components/terminal/` — barrel-exported from `index.ts`

## Build & Run

```bash
# Infrastructure (PostgreSQL + Redis) — choose one:
brew services start postgresql@16 && brew services start redis    # Native macOS
# OR
docker compose -f infra/docker-compose.yml up -d                  # Container (OrbStack recommended over Docker Desktop)

# Backend
cd backend && pdm install && pdm run dev

# Workspace install (from repo root)
pnpm install              # Installs all workspace deps

# Frontend
cd frontend && pnpm dev

# All at once
make dev-local
```

## Conventions

- **Documentation**: Everytime a message is typed or change is made into the code update the documentation with the same
- **API routes** live in `backend/app/routes/` — one file per domain (market, trade, ai, etc.)
- **Services** live in `backend/app/services/` — business logic, never in route handlers
- **Logging**: Backend uses `from app.core.logging import get_logger`; Frontend uses `import { getLogger } from "@/lib/logger"`. Logs write to `logs/` dir (gitignored). Configure via `LOG_LEVEL`, `LOG_DIR`, `LOG_FILE` env vars.
- **New UI component?** Add to `packages/solar-orb-ui/src/components/`, export from `src/index.ts`, rebuild with `pnpm build`
- **New broker?** Implement `BaseBroker` in `backend/app/services/broker_{name}.py`
- **Database migrations**: `cd backend && pdm run alembic revision --autogenerate -m "description"`
- **Environment variables**: All ports defined in `.env.port` at repo root. Add new vars to the appropriate `.env.example` file — never commit `.env`
- **Design tokens**: Source of truth is `packages/solar-orb-ui/src/tokens/` (JSON + TS). CSS tokens in `theme.css` must stay in sync.
- **AI outputs always include disclaimer**: "Not SEBI registered investment advice"
- All financial amounts use `float` for now (will migrate to `Decimal` before production)

## Testing

- Backend: `cd backend && pdm run pytest -v`
- Frontend: `cd frontend && pnpm lint && pnpm type-check`

## Documentation

Detailed docs in `docs/`: WHY.md (vision), WHAT.md (features), HOW.md (architecture), GETTING_STARTED.md (setup).
