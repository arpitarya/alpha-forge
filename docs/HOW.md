# How AlphaForge Works

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│               Next.js 15 + React 19 + TypeScript             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │Dashboard │ │ Charts   │ │Portfolio │ │   AI Chat    │   │
│  │  Panel   │ │(LW Charts│ │  View    │ │  Interface   │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│           │          │           │              │             │
│           └──────────┴───────────┴──────────────┘            │
│                         REST + WebSocket                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                     │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Auth    │ │ Market   │ │  Trade   │ │     AI       │   │
│  │ Routes   │ │  Routes  │ │  Routes  │ │   Routes     │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘   │
│       │             │            │               │           │
│  ┌────┴─────────────┴────────────┴───────────────┴───────┐  │
│  │                   SERVICE LAYER                        │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────┐  │  │
│  │  │Market Data  │ │Broker Service│ │  AI Service    │  │  │
│  │  │  Service    │ │(Zerodha/Angel│ │ (LLM + RAG)   │  │  │
│  │  └──────┬──────┘ └──────┬───────┘ └───────┬────────┘  │  │
│  └─────────┼───────────────┼─────────────────┼───────────┘  │
└────────────┼───────────────┼─────────────────┼──────────────┘
             │               │                 │
             ▼               ▼                 ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  NSE / BSE   │ │  Zerodha     │ │  OpenAI /    │
     │  Data Feeds  │ │  Kite API    │ │  LLM APIs    │
     └──────────────┘ └──────────────┘ └──────────────┘

     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  PostgreSQL  │ │    Redis     │ │   Celery     │
     │  (primary DB)│ │ (cache/pubsub│ │  (bg tasks)  │
     └──────────────┘ └──────────────┘ └──────────────┘
```

---

## Tech Stack Deep Dive

### Backend: Python 3.12 + FastAPI

**Why Python?**
- Best-in-class ecosystem for financial analysis (pandas, numpy, ta-lib)
- Excellent ML/AI libraries (LangChain, OpenAI SDK, scikit-learn)
- FastAPI provides async performance rivaling Node.js for I/O-bound work
- Indian broker SDKs (kiteconnect, smartapi) are Python-first

**Key packages:**
| Package | Purpose |
|---------|---------|
| `fastapi` | Async API framework with auto OpenAPI docs |
| `sqlalchemy` 2.0 | Async ORM with PostgreSQL |
| `alembic` | Database schema migrations |
| `pydantic` v2 | Data validation & serialization |
| `kiteconnect` | Zerodha broker API SDK |
| `pandas` + `numpy` | Data manipulation & analysis |
| `ta-lib` | 150+ technical indicators |
| `langchain` | AI/LLM orchestration, RAG pipelines |
| `celery` | Distributed task queue for background jobs |
| `httpx` | Async HTTP client for external APIs |

**Package management**: PDM with uv as resolver/installer. Lockfile: `pdm.lock`.

### Frontend: Next.js 15 + React 19 + TypeScript

**Why Next.js?**
- Server-side rendering for fast initial load
- App Router for file-based routing
- API route proxying to backend
- Excellent TypeScript support

**Key packages:**
| Package | Purpose |
|---------|---------|
| `lightweight-charts` | TradingView's open-source charting library |
| `zustand` | Lightweight state management |
| `axios` | HTTP client for API calls |
| `socket.io-client` | Real-time WebSocket communication |
| `recharts` | Charts for portfolio/analytics views |
| `tailwindcss` v4 | Utility-first CSS with terminal aesthetic |
| `lucide-react` | Icon library |

**Package management**: pnpm (strict, disk-efficient). Lockfile: `pnpm-lock.yaml`.

### Database: PostgreSQL 16

**Schema overview:**
```
users
├── id (UUID, PK)
├── email (unique, indexed)
├── hashed_password
├── full_name
├── is_active, is_verified
└── created_at, updated_at

holdings
├── id (UUID, PK)
├── user_id (FK → users)
├── symbol, exchange
├── quantity, avg_price
└── created_at

orders
├── id (UUID, PK)
├── user_id (FK → users)
├── broker_order_id
├── symbol, exchange, side
├── order_type, product
├── quantity, price, trigger_price
├── status, status_message
└── placed_at

watchlists
├── id (UUID, PK)
├── user_id (FK → users)
├── name
├── symbols (JSON array)
└── created_at
```

### Cache & Real-Time: Redis 7

- **Quote cache** — Cache frequently-accessed stock quotes (TTL: 1-5 seconds)
- **Session store** — User sessions for faster auth
- **Pub/Sub** — Real-time price updates to WebSocket clients
- **Rate limiting** — Protect against API abuse
- **Celery broker** — Message queue for background tasks

### AI: OpenAI + LangChain

**AI Architecture:**
```
User Query
    │
    ▼
┌──────────────────────────────────────┐
│           AI ORCHESTRATOR            │
│                                      │
│  1. Parse user intent               │
│  2. Determine required data sources  │
│  3. Fetch context:                   │
│     ├─ Real-time market data         │
│     ├─ Historical price (OHLCV)      │
│     ├─ Technical indicators          │
│     ├─ Fundamental data              │
│     ├─ Recent news articles          │
│     ├─ User's portfolio (if any)     │
│     └─ Regulatory filings            │
│  4. Build RAG context                │
│  5. Send to LLM with system prompt   │
│  6. Parse response + suggested actions│
│  7. Return structured response       │
└──────────────────────────────────────┘
    │
    ▼
Structured Response:
  - Natural language analysis
  - Data tables / metrics
  - Actionable buttons (Buy/Sell/Add to Watchlist)
  - Confidence score
  - Source citations
```

**System Prompt Strategy:**
The AI is configured as a seasoned Indian market analyst with:
- Deep knowledge of NSE/BSE market microstructure
- Understanding of SEBI regulations, corporate actions, taxation
- Access to real-time data via function calling
- Conservative bias (never aggressively recommend, always show risk)
- Disclaimer awareness (not SEBI-registered, educational only)

---

## Broker Integration

### Zerodha Kite Connect

```
Login Flow:
1. User clicks "Connect Broker" → Redirect to Kite login page
2. User logs in on Kite → Kite redirects back with request_token
3. Backend exchanges request_token for access_token
4. access_token stored (encrypted) for the session / day
5. All subsequent API calls use this token

API Capabilities:
├── Orders: place, modify, cancel
├── Portfolio: holdings, positions
├── Market: quotes, instruments, historical data
└── Streaming: WebSocket tick data
```

### Abstraction Layer

All brokers implement a common `BaseBroker` interface:
```python
class BaseBroker(ABC):
    async def authenticate(credentials) → bool
    async def place_order(symbol, side, qty, ...) → BrokerOrder
    async def cancel_order(order_id) → bool
    async def get_positions() → list[BrokerPosition]
    async def get_holdings() → list[BrokerPosition]
    async def get_order_history() → list[BrokerOrder]
    async def get_quote(symbol, exchange) → dict
```

This makes adding new brokers (Angel One, Upstox, Groww) a matter of implementing the interface.

---

## Security & Compliance

### Security Measures
- **JWT authentication** with short-lived tokens (30 min default)
- **bcrypt password hashing** with salt
- **CORS** restricted to frontend origin
- **Secrets in env vars** — never in code
- **Broker tokens encrypted** at rest
- **Rate limiting** on all endpoints
- **Input validation** via Pydantic (SQL injection / XSS prevention)
- **HTTPS mandatory** in production

### Regulatory Awareness
- AlphaForge is a **tool**, not a financial advisor
- Clear disclaimers on all AI outputs: "Not SEBI registered investment advice"
- No guaranteed return claims
- User data privacy — minimal data collection, no selling
- Compliance with RBI's LRS guidelines for international investing features

---

## Data Flow: Real-Time Quotes

```
NSE/BSE Market
    │
    ▼ (WebSocket / polling)
Market Data Service
    │
    ├──→ Redis Cache (TTL: 1-5s)
    │
    ├──→ Redis Pub/Sub channel: "quotes:{symbol}"
    │
    └──→ API Response (REST)

Frontend
    │
    ├──→ REST /api/v1/market/quote/{symbol}  (initial load)
    │
    └──→ WebSocket subscription               (live updates)
         └── Receives pub/sub messages from Redis
```

---

## Development Workflow

### Local (Recommended for macOS Apple Silicon)

```bash
# 1. Setup infrastructure (one-time)
bash infra/setup-local.sh             # PostgreSQL + Redis via Homebrew

# 2. Install dependencies
cd backend && pdm install             # Python deps (uses uv resolver)
cd frontend && pnpm install           # Node deps

# 3. Run migrations
cd backend && pdm run migrate         # Apply schema

# 4. Start backend
cd backend && pdm run dev             # uvicorn --reload at :8000

# 5. Start frontend
cd frontend && pnpm dev               # Next.js at :3000

# Or start both at once:
make dev-local                        # Uses overmind/honcho + Procfile

# 6. Run tests
make test

# 7. Create new migration after model changes
make db-revision msg="add watchlist table"
```

### Container (OrbStack or Docker)

```bash
docker compose -f infra/docker-compose.yml up --build
```

### GitHub Codespaces

The `.devcontainer/devcontainer.json` sets up a full cloud environment with PostgreSQL, Redis, and all dependencies pre-installed.

### Code Quality
- **Backend**: `ruff` for linting + formatting, `mypy` for type checking, `pytest` for tests — all via `pdm run`
- **Frontend**: `eslint` + `next lint`, TypeScript strict mode — all via `pnpm`
- **Pre-commit hooks** (planned): lint + format on every commit

---

## Deployment Architecture (Production)

```
                    Cloudflare (CDN + DDoS protection)
                              │
                              ▼
                    ┌──────────────────┐
                    │   Load Balancer  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Backend  │  │ Backend  │  │ Backend  │
        │ (Gunicorn│  │ (replica)│  │ (replica)│
        └──────────┘  └──────────┘  └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │PostgreSQL│  │  Redis   │  │  Celery  │
        │(Primary) │  │ Cluster  │  │ Workers  │
        └──────────┘  └──────────┘  └──────────┘
```

Target deployment: **AWS / Railway / Fly.io** depending on scale requirements.
