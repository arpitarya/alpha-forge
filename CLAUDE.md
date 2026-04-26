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
├── llm-gateway/      Publishable Python package (alphaforge-llm-gateway)
│   ├── src/alphaforge_llm_gateway/  LLMGateway, providers, router, rate_limiter, cost_guard, CLI
│   └── notebooks/    Interactive Jupyter playground for provider comparison & benchmarks
├── repo-context-mcp/ Tool-agnostic MCP server — gives Claude/Copilot/Cursor/any MCP client semantic + structural context over this repo
│   └── src/alphaforge_repo_context/  server, indexer, chunker, embeddings, watcher, tools/
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
| LLM Gateway | alphaforge-llm-gateway | 5 free providers (Gemini, Groq, HuggingFace, OpenRouter, Ollama), smart routing, $0 cost wall |
| Repo Context MCP | alphaforge-repo-context-mcp | Local stdio MCP server; pgvector-backed semantic + structural repo context for Claude/Copilot/Cursor/any MCP client |
| Brokers | Abstract BaseBroker interface | Zerodha first, then Angel One, Upstox |
| Local infra | brew services (Postgres, Redis) | Containers optional via OrbStack |
| Browser MCP | Playwright MCP | Copilot can screenshot/inspect Chrome via `.vscode/settings.json` |
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
- `backend/app/services/screener.py` — Screener picks storage/retrieval service
- `backend/app/services/llm_gateway.py` — LLM Gateway thin wrapper (wires to settings)
- `backend/app/routes/screener.py` — Screener API endpoints (POST/GET picks, list dates)
- `backend/app/routes/llm.py` — LLM Gateway API endpoints (complete, analyze, providers, benchmark)
- `screener/notebooks/screener_pipeline.ipynb` — Interactive Jupyter notebook for full screener pipeline
- `frontend/src/app/page.tsx` — Terminal landing page (Solar Terminal dashboard)
- `frontend/src/components/terminal/ScreenerPicks.tsx` — Screener picks display component (live data from backend)
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
- `llm-gateway/src/alphaforge_llm_gateway/__init__.py` — LLM Gateway barrel export (LLMGateway, LLMResponse, QueryType)
- `llm-gateway/src/alphaforge_llm_gateway/gateway.py` — Main LLMGateway class (from_env, complete, analyze_screener)
- `llm-gateway/src/alphaforge_llm_gateway/cli.py` — CLI: analyze-screener, explain-picks, chat, benchmark, providers
- `llm-gateway/notebooks/llm_gateway_playground.ipynb` — Interactive notebook for provider comparison & benchmarks
- `repo-context-mcp/src/alphaforge_repo_context/server.py` — MCP server entry (stdio); exposes `search_code`, `get_symbol`, `module_overview`, `recent_changes`, `read_file_range`
- `repo-context-mcp/src/alphaforge_repo_context/indexer.py` — Walk → chunk → embed → pgvector; CLI `alphaforge-repo-context-index`
- `repo-context-mcp/src/alphaforge_repo_context/chunker.py` — AST (Python), regex (TS/TSX), section (Markdown), sliding-window fallback
- `repo-context-mcp/src/alphaforge_repo_context/db.py` — `repo_chunks` ORM model + `init_schema()`
- `repo-context-mcp/README.md` — Wire-up snippets for Claude Code, VS Code/Copilot, Cursor, Cline, Zed, Windsurf
- `.python-version` — Python version for pyenv (3.14.2)
- `.nvmrc` — Node.js version for nvm
- `.npmrc` — pnpm/npm configuration (exact versions, engine-strict)
- `backend/pdm.toml` — PDM project config (repo-root venv, uv backend)
- `backend/pip.conf` — pip configuration (require-virtualenv)
- `pnpm-workspace.yaml` — Workspace root definition
- `.env.port` — All service ports in one file
- `.vscode/settings.json` — VS Code workspace settings (MCP server config for Playwright)
- `.env.example` — Root environment template
- `backend/.env.example` — Backend environment template
- `frontend/.env.example` — Frontend environment template

## Commands

```bash
# Full repo setup (prereqs, venv, all deps, env files, dirs)
./setup.sh                # One command to set up everything
./setup.sh --help         # Show all setup.sh options

# Setup — granular
./setup.sh --prereqs      # Check/install pyenv, nvm, pnpm, pdm
./setup.sh --venv         # Create .venv from .python-version
./setup.sh --backend      # Backend deps (PDM → .venv)
./setup.sh --frontend     # Frontend + workspace deps (pnpm) + build solar-orb-ui
./setup.sh --screener     # Screener ML deps (pip → .venv)
./setup.sh --env          # Scaffold .env files from examples
./setup.sh --dirs         # Create log/data/model directories
./setup.sh --db           # Setup local PostgreSQL + Redis (macOS Homebrew)

# Backend
cd backend && pdm run dev           # Start server (uvicorn --reload)
cd backend && pdm run pytest -v     # Tests
cd backend && pdm run ruff check .  # Lint

# Frontend
cd frontend && pnpm dev             # Dev server
cd frontend && pnpm lint            # Lint
cd frontend && pnpm type-check      # TypeScript check

# UI Package
cd packages/solar-orb-ui && pnpm build   # Build ESM + CJS + DTS
cd packages/solar-orb-ui && pnpm dev     # Watch mode

# Copilot Browser Integration
just setup-mcp                           # Install Playwright Chromium + MCP config

# Infrastructure
./setup.sh --db                                                 # macOS native (Homebrew)
# OR: docker compose -f infra/docker-compose.yml up -d          # via OrbStack

# Migrations
cd backend && pdm run alembic upgrade head
cd backend && pdm run alembic revision --autogenerate -m "description"

# Screener pipeline
./setup.sh --pipeline     # Full data → train → backtest
./setup.sh --scan         # Daily live scan

# Cleanup
./clean.sh                # Remove build artifacts and bytecode (keeps venv + node_modules)
./clean.sh --cache        # Remove only tool caches
./clean.sh --venv         # Remove Python venv
./clean.sh --backend      # Deep-clean backend (artifacts, caches, venv)
./clean.sh --frontend     # Deep-clean frontend (.next, node_modules)
./clean.sh --all          # Nuclear clean — removes everything (run setup.sh to restore)

# LLM Gateway
just llm-gateway-install                                        # Install package into .venv
just llm-providers                                              # Show provider health + quota
just llm-benchmark                                              # Benchmark all providers
python -m alphaforge_llm_gateway chat                           # Interactive chat
python -m alphaforge_llm_gateway analyze-screener -f picks.txt  # Analyze screener output

# Repo Context MCP (tool-agnostic: Claude, Copilot, Cursor, etc.)
cd repo-context-mcp && pdm install                              # Install deps
cd repo-context-mcp && pdm run index --full                     # Build initial vector index
cd repo-context-mcp && pdm run index --watch                    # Watch + incremental reindex
cd repo-context-mcp && pdm run serve                            # Run MCP server (stdio)
alphaforge-repo-context-mcp                                     # Same server (after `pdm install`)
```

## Guardrails
- Never commit `.env` files or API keys
- All AI outputs must include financial disclaimer
- Everytime a message is typed or change is made into the code update the documentation with the same
- When planning a new module or feature, create a `PLAN.md` inside that module's directory with the full plan, goals, phases, and design decisions; then link it from the root-level `PLAN.md` so all plans can be tracked from one place
- When a new module or feature is built, create an `implement.txt` inside that module's directory logging what was built, decisions made, and status; then link it from the root-level `implement.txt` so all modules can be tracked from one place
- Broker tokens encrypted at rest
- CORS restricted to frontend origin only
- No guaranteed return claims anywhere in code or UI
- Follow the file layout + naming rules in [structure/](structure/README.md). Each top-level module has its own `files.md` and `variables.md`; consult them before creating a new file or naming a new symbol.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- For cross-module "how does X relate to Y" questions, prefer `graphify query "<question>"`, `graphify path "<A>" "<B>"`, or `graphify explain "<concept>"` over grep — these traverse the graph's EXTRACTED + INFERRED edges instead of scanning files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
