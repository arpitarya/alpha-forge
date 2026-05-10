# AlphaForge Backend API

Base URL: `http://localhost:8000/api/v1`

Interactive docs: `http://localhost:8000/docs` (Swagger) · `http://localhost:8000/redoc`

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service liveness check |

**Response**
```json
{ "status": "healthy", "service": "alphaforge-api" }
```

---

## Market  `/market`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/market/quote/{symbol}` | Real-time quote for an NSE/BSE symbol |
| GET | `/market/indices` | Major indices — NIFTY 50, SENSEX, BANK NIFTY |
| GET | `/market/search` | Search stocks, ETFs, mutual funds |
| GET | `/market/history/{symbol}` | OHLCV price history for charting |

**Query params**

`GET /market/search`
- `q` — search term (1–50 chars, required)

`GET /market/history/{symbol}`
- `interval` — `1m | 5m | 15m | 1h | 1d | 1w | 1M` (default `1d`)
- `period` — `1d | 5d | 1M | 3M | 6M | 1y | 5y | max` (default `1y`)

---

## Portfolio  `/portfolio`

### Holdings & analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/portfolio/holdings` | Aggregated holdings across all sources |
| GET | `/portfolio/treemap` | Squarified treemap layout for the portfolio |
| GET | `/portfolio/rebalance` | Drift vs. target allocation + suggestions |

All three accept an optional `?source=<slug>` query param to scope results to one broker.

**`GET /portfolio/holdings` response shape**
```json
{
  "totals": { "invested": 0, "current_value": 0, "pnl": 0, "pnl_pct": 0, "count": 0 },
  "allocation": [{ "asset_class": "equity", "value": 0, "pct": 0 }],
  "holdings": [{ "symbol": "RELIANCE", "quantity": 120, "avg_price": 2410, ... }],
  "disclaimer": "..."
}
```

### Broker sources  `/portfolio/sources`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/portfolio/sources` | List all configured broker sources |
| GET | `/portfolio/sources/{slug}` | Details for a single source |
| POST | `/portfolio/sources/{slug}/sync` | Trigger live sync for an API source (e.g. Zerodha) |
| POST | `/portfolio/sources/sync-all` | Sync all API sources in parallel |

**Source slugs:** `zerodha`

**`GET /portfolio/sources` response shape**
```json
{
  "sources": [
    {
      "slug": "zerodha",
      "label": "Zerodha (Kite)",
      "kind": "api",
      "status": "ready",
      "holdings_count": 13,
      "last_synced_at": "2026-05-10T08:00:07Z",
      "error_message": null,
      "notes": "..."
    }
  ]
}
```

**`POST /portfolio/sources/{slug}/sync` response shape**
```json
{
  "source": "zerodha",
  "holdings_count": 13,
  "holdings": [...],
  "info": { ... }
}
```

---

## Dashboard  `/dashboard`

Read-only feeds for the terminal home screen.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/ticker` | Scrolling ticker items (symbol, price, change) |
| GET | `/dashboard/watchlist` | Watchlist with labels and price tone |
| GET | `/dashboard/risk` | Risk meter bar data + confidence score |
| GET | `/dashboard/brief` | Terminal brief blocks (AI-generated summary) |
| GET | `/dashboard/stats` | Net worth, today's P&L, and confidence stat cards |

---

## AI  `/ai`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ai/chat` | RAG-backed chat with portfolio + market context |
| POST | `/ai/analyze` | Deep analysis for a given stock symbol |
| GET | `/ai/screener` | Return latest screener picks via AI strategy |
| GET | `/ai/sentiment/{symbol}` | Sentiment score for a symbol (news-based) |
| GET | `/ai/memory/search` | Semantic search over past picks + conversation turns |

**`POST /ai/chat` body**
```json
{
  "messages": [{ "role": "user", "content": "..." }],
  "context": "optional extra context string"
}
```

**`POST /ai/analyze` body**
```json
{ "symbol": "RELIANCE", "analysis_type": "fundamental" }
```

**`GET /ai/screener` query params**
- `strategy` — e.g. `momentum` (default)

**`GET /ai/memory/search` query params**
- `q` — natural language query (required)
- `symbol` — filter picks by symbol (optional)
- `top_k` — results per category, 1–20 (default `5`)

---

## Screener  `/screener`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/screener/picks` | Push a batch of ML screener picks from the pipeline |
| POST | `/screener/picks/embed-backfill` | Backfill embeddings for all stored picks (background) |
| GET | `/screener/picks` | Fetch latest (or date-specific) screener picks |
| GET | `/screener/dates` | List all available scan dates |

**`POST /screener/picks` body**
```json
{
  "scan_date": "2026-05-10",
  "model_type": "xgboost_v2",
  "picks": [{ "symbol": "RELIANCE", "score": 0.91, ... }]
}
```

**`GET /screener/picks` query params**
- `date` — scan date `YYYY-MM-DD` (optional; returns latest if omitted)

---

## LLM Gateway  `/llm`

Multi-provider AI completion (Gemini, Groq, HuggingFace, OpenRouter, Ollama).

| Method | Path | Description |
|--------|------|-------------|
| POST | `/llm/complete` | Generic multi-provider completion |
| POST | `/llm/analyze-screener` | Analyze raw screener output text |
| POST | `/llm/explain-picks` | Explain a set of screener picks in plain language |
| GET | `/llm/providers` | Provider health and quota status |
| GET | `/llm/benchmark` | Latest benchmark result (or prompt to run one) |
| POST | `/llm/benchmark/run` | Start a background provider benchmark |

**`POST /llm/complete` body**
```json
{
  "messages": [{ "role": "user", "content": "..." }],
  "query_type": "chat",
  "provider": null,
  "model": null,
  "temperature": 0.7,
  "max_tokens": 1024
}
```

**`POST /llm/analyze-screener` and `/llm/explain-picks` body**
```json
{ "raw_output": "raw screener text or picks JSON..." }
```

**LLM response shape**
```json
{
  "content": "...",
  "model": "gemini-1.5-flash",
  "provider": "gemini",
  "tokens_used": 512,
  "latency_ms": 820,
  "cost": 0.0
}
```

---

## Error responses

All endpoints follow a standard FastAPI error envelope:

```json
{ "detail": "Human-readable error message" }
```

Common HTTP status codes:
- `400` — bad request (invalid params, sync failed)
- `404` — unknown source slug or resource not found
- `422` — request body validation error (Pydantic)
- `500` — unexpected server error

---

> **Disclaimer:** AlphaForge is a personal research tool. Nothing here constitutes SEBI-registered investment advice.
