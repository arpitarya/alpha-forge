# CLAUDE.md — Context for Claude Code

## Project

**AlphaForge** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Built for personal use — not a SaaS product. Self-hosted, open-source, MIT licensed.

## Repository Structure

```
alpha-forge/
├── backend/          Python 3.14 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt security
│   ├── app/models/   SQLAlchemy ORM: User, Holding, Order, Watchlist
│   ├── app/routes/   FastAPI routers: health, auth, market, portfolio, ai, trade
│   ├── app/services/ Business logic: broker_base (ABC), broker_zerodha, ai_service, market_data
│   ├── alembic/      Database migrations
│   └── tests/        Pytest suite
├── packages/
│   ├── logger-py/    Publishable Python logger package (alphaforge-logger)
│   │   └── src/alphaforge_logger/  setup_logging(), get_logger()
│   ├── logger-node/  Publishable Node/TS logger package (@alphaforge/logger)
│   │   └── src/      createLogger(), getLogger() — pino-based
│   └── solar-orb-ui/ Publishable UI component library (@alphaforge/solar-orb-ui)
│       ├── src/components/  Button, Input, Card, Badge, Icon, Text
│       └── src/styles/      fonts.css, theme.css, base.css (design tokens + base styles)
├── frontend/         Next.js 15 (App Router) + React 19 + TypeScript + Tailwind v4
│   ├── src/app/      Pages and layouts (Solar Terminal theme)
│   ├── src/components/  UI components (layout, terminal, dashboard, ai, solar-orb)
│   │   ├── terminal/    Terminal landing page components (SolarOrb, AlphaBrief,
│   │   │                TerminalWatchlist, PortfolioCards, RiskAnalysis, VoiceFooter)
│   │   └── solar-orb/   Re-exports from @alphaforge/solar-orb-ui package
│   └── src/lib/      API client (axios), Zustand store, React Query hooks
├── infra/            Infrastructure configs (docker-compose for services, devcontainer)
├── docs/             WHY.md, WHAT.md, HOW.md, GETTING_STARTED.md
└── design/           Design system & Gemini Stitch tokens
```

## Tech Decisions

| Area | Choice | Notes |
|------|--------|-------|
| Python pkg mgr | PDM + uv | `pdm install` uses uv; installs into repo-root `.venv` (see `backend/pdm.toml`) |
| Python version | pyenv | Pinned in `.python-version` (3.14.2) |
| Node pkg mgr | pnpm | Lockfile: `pnpm-lock.yaml`; config in `.npmrc` |
| Node version | nvm | Pinned in `.nvmrc` |
| Monorepo | pnpm workspaces | `pnpm-workspace.yaml` at root; `packages/*` + `frontend` |
| UI library | @alphaforge/solar-orb-ui | Publishable package built with tsup (ESM + CJS + DTS) |
| Logging (Python) | alphaforge-logger | Rotating file + console, env-configurable |
| Logging (Node) | @alphaforge/logger | Pino-based, file + console, publishable tsup pkg |
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
- `@alphaforge/solar-orb-ui` — design system package with components, fonts, and theme tokens
- Biome v2 for formatting/linting; ESLint v9 flat config for Next.js rules
- TanStack React Query v5 for data fetching (hooks in `src/lib/queries.ts`)

## Key Files
- `backend/app/main.py` — FastAPI app factory
- `backend/app/core/config.py` — All environment variables
- `backend/app/core/logging.py` — Backend logging setup (wraps alphaforge-logger)
- `backend/app/services/broker_base.py` — Abstract broker interface (implement this for new brokers)
- `frontend/src/app/page.tsx` — Terminal landing page (Solar Terminal dashboard)
- `frontend/src/lib/api.ts` — Backend API client
- `frontend/src/lib/logger.ts` — Frontend logging setup (wraps @alphaforge/logger)
- `packages/logger-py/src/alphaforge_logger/logger.py` — Python logger package core
- `packages/logger-node/src/logger.ts` — Node/TS logger package core
- `frontend/src/app/globals.css` — Theme variables (Solar Terminal design tokens)
- `frontend/src/components/terminal/` — Terminal page component package
- `packages/solar-orb-ui/src/index.ts` — UI library barrel export (Button, Input, Card, Badge, Icon, Text)
- `packages/solar-orb-ui/src/styles/theme.css` — Tailwind v4 design tokens (CSS)
- `packages/solar-orb-ui/src/tokens/index.ts` — Design tokens (TypeScript)
- `packages/solar-orb-ui/src/tokens/tokens.json` — Design tokens (JSON, machine-readable)
- `packages/solar-orb-ui/tsup.config.ts` — Package build config
- `.python-version` — Python version for pyenv (3.14.2)
- `.nvmrc` — Node.js version for nvm
- `.npmrc` — pnpm/npm configuration (exact versions, engine-strict)
- `backend/pdm.toml` — PDM project config (repo-root venv, uv backend)
- `backend/pip.conf` — pip configuration (require-virtualenv)
- `pnpm-workspace.yaml` — Workspace root definition
- `.env.port` — All service ports in one file
- `.env.example` — Root environment template
- `backend/.env.example` — Backend environment template
- `frontend/.env.example` — Frontend environment template

## Commands

```bash
# Backend
cd backend && pdm install           # Install deps (into repo-root .venv/)
cd backend && pdm run dev           # Start server (uvicorn --reload)
cd backend && pdm run pytest -v     # Tests
cd backend && pdm run ruff check .  # Lint

# Frontend
cd frontend && pnpm install         # Install deps
cd frontend && pnpm dev             # Dev server
cd frontend && pnpm lint            # Lint
cd frontend && pnpm type-check      # TypeScript check

# UI Package
cd packages/solar-orb-ui && pnpm build   # Build ESM + CJS + DTS
cd packages/solar-orb-ui && pnpm dev     # Watch mode

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
- Everytime a message is typed or change is made into the code update the documentation with the same
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only
- No guaranteed return claims anywhere in code or UI
