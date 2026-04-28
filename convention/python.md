# Python Convention

## Filename grammar

```
<domain>_<role>.py
```

`<domain>` = the noun the file is about (`portfolio`, `auth`, `zerodha_kite`).
`<role>`   = one of the suffixes below. The suffix is **mandatory**.

## Role suffixes

| Suffix | Holds | Imports allowed | Line cap |
|---|---|---|---|
| `*_routes.py` | FastAPI route handlers (`@router.get`, `@router.post`) | `*_service`, `*_schemas`, `*_deps` | 100 |
| `*_service.py` | Business logic, orchestration, side-effecting calls | `*_repo`, `*_models`, `*_utils`, other modules' services via their `__init__` | 100 |
| `*_repo.py` | DB queries / data access (SQLAlchemy `select(...)`) | `*_models` | 100 |
| `*_models.py` | SQLAlchemy ORM `Mapped` classes — one table per file when possible | `app.core.database` | 100 |
| `*_schemas.py` | Pydantic request/response schemas (no ORM) | nothing internal | 100 |
| `*_utils.py` | Pure functions, no I/O, no state | stdlib + third-party only | **50** |
| `*_helper.py` | Stateful helpers — login flows, retry/backoff, session caches. Sits between `*_utils.py` (pure) and `*_service.py` (orchestration) | stdlib + third-party + own module's `*_utils`, `*_types` | 100 |
| `*_types.py` | TypeAlias, Enum, Protocol — no logic | stdlib `typing` | 50 |
| `*_constants.py` | Module-scoped constants (`UPPER_SNAKE`) | stdlib only | 50 |
| `*_deps.py` | FastAPI `Depends` callables | `app.core.*`, `*_service` | 50 |
| `*_errors.py` | Custom exception classes | nothing internal | 50 |
| `*_config.py` | Module-scoped settings (subclass of `BaseSettings`) | `pydantic_settings` | 50 |
| `*_test.py` / `test_*.py` | Pytest tests | anything | 100 |

## Layout

Every feature module under `backend/app/modules/<name>/` follows this skeleton:

```
backend/app/modules/portfolio/
├── __init__.py              # re-exports `router`
├── portfolio_routes.py      # /api/v1/portfolio/*
├── portfolio_service.py     # PortfolioService
├── portfolio_repo.py        # holdings_by_user(), upsert_holding()
├── portfolio_models.py      # Holding, Order, Watchlist  (ORM)
├── portfolio_schemas.py     # HoldingOut, RebalanceRequest  (Pydantic)
└── portfolio_utils.py       # ≤ 50 lines of pure helpers
```

If you have only one ORM model and a tiny service, you can collapse `portfolio_repo.py` into `portfolio_service.py` — but never the other way around (don't put SQL in routes).

## Per-package files (legitimate exceptions to `<domain>_<role>`)

Some modules contain a **registry of N implementations** of one role. Each implementation gets a file named after the implementation, not after the role. Example:

```
backend/app/modules/brokers/
├── base.py               # BrokerSource ABC
├── registry.py           # SOURCES dict
├── zerodha_kite.py       # ZerodhaKiteSource
├── groww.py              # GrowwSource
└── csv_sources.py        # ZerodhaCSVSource, GrowwCSVSource, ...
```

The convention doesn't apply when the file IS the implementation of an interface and its name needs to identify the implementation. **This exception must be obvious** — i.e. there's a `base.py` in the same folder that defines what they implement.

## Imports

- Always absolute: `from app.modules.portfolio.portfolio_service import PortfolioService`
- One module's `__init__.py` is its **public surface** — other modules only import from `app.modules.<name>` (the package), never from a sibling's internal `*_repo.py` or `*_utils.py`.
- A module never imports from another module's `*_routes.py`. Routes are leaves.

## Line-count discipline

If a `*_service.py` is hitting 100, ask:
1. Are there pure helpers I can extract into `*_utils.py`? (≤ 50 lines)
2. Are there DB queries that belong in `*_repo.py`?
3. Are there schemas inline that belong in `*_schemas.py`?

If after that it's still over 100, **split the service**: `portfolio_sync_service.py` + `portfolio_query_service.py`. Two narrow files beat one fat one.

## Ruff config (already enforced)

- `line-length = 100` (per character, separate from line-count)
- Absolute imports only
- All public callables get type hints
