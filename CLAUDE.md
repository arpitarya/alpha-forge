# CLAUDE.md — Context for Claude Code

## Project

**AlphaForge** — Personal AI-powered portfolio management & investment terminal for Indian markets.
Built for personal use — not a SaaS product. Self-hosted, open-source, MIT licensed.

## Repository Structure

```
alpha-forge/
├── backend/          Python 3.14 + FastAPI + SQLAlchemy async
│   ├── app/core/     Config (pydantic-settings), DB engine, JWT/bcrypt, env_loader
│   ├── app/modules/  Feature modules — each owns its routes/service/models
│   │   ├── health/      /api/v1/* health endpoint
│   │   ├── auth/        routes + User ORM
│   │   ├── market/      routes + market_data service
│   │   ├── portfolio/   routes + Holding/Order/Watchlist ORM
│   │   ├── brokers/     pluggable BrokerSource adapters (Zerodha Kite/Coin, Groww, Angel One, Wint, Dezerv) + aggregator + registry. Used by portfolio routes
│   │   ├── memory/      EmbeddingService + MemoryService + ScreenerPickEmbedding/ConversationMemory ORM. Used by ai + screener
│   │   ├── ai/          routes + AIService (RAG, sentiment, screener Q&A)
│   │   ├── llm/         routes + LLMGateway thin wrapper
│   │   ├── screener/    routes + ScreenerService
│   │   ├── trade/       routes (paper/live trade endpoints)
│   │   └── dashboard/   routes (cross-module aggregation)
│   ├── app/main.py   FastAPI app factory; mounts api_router from app.modules
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
| Python pkg mgr | uv (workspace) | Single `uv.lock` at repo root; members declared in `[tool.uv.workspace]`. One `.venv/` shared across backend, screener, llm-gateway, logger-py |
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
- `backend/app/modules/__init__.py` — registers every feature router under `/api/v1/*`
- `backend/app/modules/brokers/base.py` — `BrokerSource` ABC; implement for new brokers
- `backend/app/modules/brokers/registry.py` — broker source registry (slug → class)
- `backend/app/modules/screener/service.py` — Screener picks storage/retrieval
- `backend/app/modules/screener/routes.py` — Screener API endpoints
- `backend/app/modules/llm/service.py` — LLM Gateway thin wrapper
- `backend/app/modules/llm/routes.py` — LLM Gateway API endpoints
- `backend/app/modules/memory/service.py` — `MemoryService` (RAG retrieval over picks + chats)
- `backend/app/modules/memory/embedding.py` — `EmbeddingService` (Gemini text-embedding-004)
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
- `pyproject.toml` (repo root) — uv workspace definition + `[tool.uv.sources]` for local deps
- `uv.lock` (repo root) — single lockfile for all Python workspace members
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
./setup.sh --prereqs      # Check/install pyenv, nvm, pnpm, uv
./setup.sh --venv         # Create .venv via `uv venv` (reads .python-version)
./setup.sh --backend      # Sync the entire Python workspace (uv sync) + Playwright browsers
./setup.sh --frontend     # Frontend + workspace deps (pnpm) + build solar-orb-ui
./setup.sh --screener     # Alias for --backend (screener is a workspace member now)
./setup.sh --env          # Scaffold .env files from examples
./setup.sh --dirs         # Create log/data/model directories
./setup.sh --db           # Setup local PostgreSQL + Redis (macOS Homebrew)

# Python Workspace (uv)
uv sync                              # Install/refresh every workspace member into .venv
uv lock                              # Refresh uv.lock without installing
uv add httpx --package alphaforge-backend   # Add a dep to a specific member
just sync                            # Same as `uv sync` (justfile shortcut)

# Backend
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd backend && uv run pytest -v
uv run ruff check .

# Backend Debugging (VS Code)
# Option A — launch directly: pick "Backend: FastAPI (uvicorn, debug)" in the Run & Debug panel (F5)
# Option B — attach to a running process:
just backend-debug                  # Starts uvicorn under debugpy (waits on :5678)
                                    # Then pick "Backend: Attach (debugpy on :5678)" in VS Code
# Option C — debug current pytest file: open a test file → "Backend: Pytest (current file)"

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
cd backend && uv run alembic upgrade head
cd backend && uv run alembic revision --autogenerate -m "description"

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
