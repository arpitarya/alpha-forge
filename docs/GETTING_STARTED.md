# Getting Started — Developer Setup

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | `brew install python@3.12` |
| Node.js | 22+ | `brew install node` |
| Docker & Compose | Latest | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| Git | Latest | `brew install git` |

---

## Option 1: Docker (Recommended)

The fastest way to get everything running:

```bash
# 1. Clone the repository
git clone https://github.com/your-username/alpha-forge.git
cd alpha-forge

# 2. Copy environment file and add your keys
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (at minimum, set a strong SECRET_KEY)

# 3. Start everything
docker compose up --build

# Backend API: http://localhost:8000
# API Docs:    http://localhost:8000/docs
# Frontend:    http://localhost:3000
# PostgreSQL:  localhost:5432
# Redis:       localhost:6379
```

---

## Option 2: Local Development

For a faster dev loop with hot reload:

### 1. Start Infrastructure

```bash
# Start PostgreSQL and Redis via Docker
make db-up
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: Open http://localhost:8000/docs — you should see the Swagger UI.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Verify: Open http://localhost:3000 — you should see the AlphaForge dashboard.

---

## Configuration

### Required Environment Variables

The only **required** variables for basic operation:

```bash
SECRET_KEY=<a-random-string-for-JWT>
DATABASE_URL=postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge
REDIS_URL=redis://localhost:6379/0
```

### Optional — AI Features

```bash
OPENAI_API_KEY=sk-...       # Required for AI chat and analysis
OPENAI_MODEL=gpt-4o         # Or gpt-4o-mini for cheaper testing
```

### Optional — Broker Integration

```bash
# Zerodha Kite (get from https://developers.kite.trade)
KITE_API_KEY=your_key
KITE_API_SECRET=your_secret
```

---

## Common Commands

```bash
make help              # Show all available commands
make dev               # Start everything with Docker
make backend           # Run backend locally
make frontend          # Run frontend locally
make test              # Run all tests
make lint              # Lint backend + frontend
make format            # Auto-format backend code
make db-migrate        # Apply pending migrations
make db-revision msg="description"  # Create new migration
```

---

## Project Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory
│   ├── core/
│   │   ├── config.py        # Pydantic settings (env vars)
│   │   ├── database.py      # SQLAlchemy async engine
│   │   └── security.py      # JWT + password hashing
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── portfolio.py     # Holding, Order, Watchlist models
│   ├── routes/
│   │   ├── __init__.py      # Central router registry
│   │   ├── health.py        # GET /health
│   │   ├── auth.py          # POST /auth/register, /auth/login
│   │   ├── market.py        # GET /market/quote, /indices, /history
│   │   ├── portfolio.py     # GET /portfolio/summary, /positions
│   │   ├── ai.py            # POST /ai/chat, /ai/analyze
│   │   └── trade.py         # POST /trade/order
│   └── services/
│       ├── broker_base.py   # Abstract broker interface
│       ├── broker_zerodha.py# Zerodha Kite implementation
│       ├── ai_service.py    # LLM orchestration
│       └── market_data.py   # Market data fetcher
├── alembic/                 # Database migrations
├── tests/                   # Pytest test suite
├── Dockerfile
├── pyproject.toml
└── .env.example

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Dashboard page
│   │   └── globals.css      # Global styles + theme
│   ├── components/
│   │   ├── layout/          # Header, Sidebar
│   │   ├── dashboard/       # MarketOverview, Watchlist
│   │   └── ai/              # AIChat component
│   └── lib/
│       ├── api.ts           # Axios API client
│       └── store.ts         # Zustand state management
├── package.json
├── tsconfig.json
├── next.config.mjs
└── Dockerfile
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` |
| Port 3000 already in use | `lsof -ti:3000 \| xargs kill` |
| Docker PostgreSQL won't start | `docker compose down -v && docker compose up` |
| `ta-lib` install fails | Install system lib: `brew install ta-lib` |
| Frontend can't reach backend | Check CORS config in `.env` and Next.js rewrite proxy |
| Alembic migration fails | Ensure DB is running: `make db-up` |

---

## Next Steps

Once the base setup is running:

1. **Explore the API** at http://localhost:8000/docs
2. **Try the AI chat** (once you add an OpenAI key)
3. **Connect a broker** (get Zerodha Kite API key from developers.kite.trade)
4. **Check the roadmap** in [WHAT.md](WHAT.md) for upcoming features
5. **Contribute** — pick an issue, create a PR!
