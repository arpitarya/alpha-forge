# What AlphaForge Is

## One-liner

**An AI-powered Bloomberg Terminal for Indian investors** — combining market data, analysis, and trade execution in a single platform.

---

## Core Features

### 1. Real-Time Market Dashboard
- **Live market indices** — NIFTY 50, SENSEX, BANK NIFTY, sector indices
- **Stock quotes** — Real-time price, volume, bid/ask from NSE & BSE
- **Customisable watchlists** — Track your favourite stocks across multiple lists
- **Market breadth** — Advance/decline, 52-week highs/lows, volume leaders

### 2. Professional Charting
- **Candlestick charts** with multiple timeframes (1m → monthly)
- **50+ technical indicators** — RSI, MACD, Bollinger Bands, Supertrend, VWAP, etc.
- **Drawing tools** — Trendlines, Fibonacci, support/resistance zones
- **Multi-chart layout** — Compare stocks side-by-side
- Powered by **TradingView Lightweight Charts**

### 3. AI-Powered Analysis Engine
- **Conversational AI** — Ask questions in natural language
  - "Is INFY overvalued?"
  - "Show me stocks with RSI < 30 and PE < 15"
  - "Compare TCS vs INFY for long-term investment"
- **Stock analysis reports** — AI-generated comprehensive reports combining:
  - Technical analysis (indicators, patterns, chart analysis)
  - Fundamental analysis (financials, ratios, peer comparison)
  - News sentiment (NLP on recent articles)
  - Institutional activity (FII/DII data, bulk/block deals)
- **AI screener** — Find stocks matching strategies:
  - Momentum, Value, Growth, Dividend, Breakout
  - Custom criteria in natural language
- **Portfolio advisor** — AI reviews your portfolio and suggests rebalancing
- **Risk analysis** — Portfolio risk metrics, correlation analysis, max drawdown scenarios

### 4. Trade Execution
- **Connected broker accounts** — Link Zerodha, Angel One, Upstox
- **One-click trading** — Place orders directly from analysis/chat
- **Order types** — Market, Limit, Stop-Loss, Stop-Loss Market
- **Product types** — CNC (delivery), MIS (intraday), NRML (F&O)
- **Order book** — View pending, executed, cancelled orders
- **Position tracking** — Real-time P&L for open positions

### 5. Portfolio Management
- **Unified portfolio view** — All holdings across brokers
- **Performance tracking** — Daily, weekly, monthly, yearly returns
- **Sector allocation** — Visual breakdown of exposure
- **Dividend tracker** — Track dividend income
- **Tax implications** — STCG/LTCG computations for tax planning

### 6. News & Sentiment
- **Aggregated news feed** — From MoneyControl, Economic Times, LiveMint, etc.
- **AI-summarised headlines** — Get the gist without reading 20 articles
- **Per-stock sentiment score** — NLP-derived sentiment from news & social media
- **Alerts** — Get notified on breaking news for your watchlist stocks

---

## Scope & Boundaries

### In Scope (Phase 1 — India)
| Feature | Status |
|---------|--------|
| NSE & BSE equities | ✅ Planned |
| NIFTY & SENSEX indices | ✅ Planned |
| F&O (Futures & Options) | ✅ Planned |
| Mutual Funds (NAV, SIP tracking) | ✅ Planned |
| Zerodha Kite integration | ✅ Planned |
| Angel One integration | 🔜 Phase 1.1 |
| AI chat & analysis | ✅ Planned |
| Technical & fundamental analysis | ✅ Planned |
| News sentiment | ✅ Planned |

### In Scope (Phase 2 — Expand)
| Feature | Status |
|---------|--------|
| Commodities (MCX) | 🔜 Phase 2 |
| Currency pairs (USD/INR, etc.) | 🔜 Phase 2 |
| Crypto (via Indian exchanges) | 🔜 Phase 2 |
| Upstox, Groww broker integration | 🔜 Phase 2 |
| Options chain analyzer | 🔜 Phase 2 |
| Backtesting engine | 🔜 Phase 2 |
| Paper trading | 🔜 Phase 2 |

### In Scope (Phase 3 — Global)
| Feature | Status |
|---------|--------|
| US markets (NYSE, NASDAQ) | 🔜 Phase 3 |
| LRS investing from India | 🔜 Phase 3 |
| Multi-currency portfolio | 🔜 Phase 3 |
| Global ETFs | 🔜 Phase 3 |
| Interactive Brokers integration | 🔜 Phase 3 |

### Out of Scope (for now)
- Fully automated trading bots (AlphaForge assists, user decides)
- Financial advisory services (SEBI RIA registration not planned)
- Proprietary brokerage / order routing
- Mobile app (web-first; responsive PWA later)

---

## Roadmap

```
Q2 2026  ──────────────────────────────────────────
  ✦ Base platform setup (backend + frontend + Docker)
  ✦ Health check, auth, core API skeleton
  ✦ Market data integration (NSE quotes & indices)
  ✦ Basic charting with Lightweight Charts
  ✦ AI chat MVP (OpenAI + market context)

Q3 2026  ──────────────────────────────────────────
  ✦ Zerodha Kite broker integration (auth, orders, positions)
  ✦ Portfolio dashboard with real holdings
  ✦ AI stock analysis (technical + fundamental)
  ✦ News aggregation & sentiment analysis
  ✦ Watchlist with real-time prices (WebSocket)

Q4 2026  ──────────────────────────────────────────
  ✦ F&O support (options chain, Greeks, strategy builder)
  ✦ AI screener (momentum, value, growth strategies)
  ✦ Angel One broker integration
  ✦ Alerts & notifications
  ✦ Paper trading mode

H1 2027  ──────────────────────────────────────────
  ✦ Backtesting engine
  ✦ Mutual fund tracking & SIP analysis
  ✦ Commodities (MCX)
  ✦ Crypto (Indian exchanges)
  ✦ Mobile-responsive PWA

H2 2027  ──────────────────────────────────────────
  ✦ US markets integration
  ✦ LRS investing support
  ✦ Multi-currency portfolio
  ✦ Self-hosted LLM option (Llama, Mistral)
  ✦ Community plugins / extensions
```

---

## User Flows

### Primary Flow: AI-Assisted Stock Analysis → Trade

```
User opens AlphaForge
  → Sees dashboard with market overview
  → Types "Analyze TCS" in AI chat
  → AI returns comprehensive analysis with recommendation
  → User clicks [Place Buy Order]
  → Order form pre-filled (symbol, suggested price)
  → User confirms → order placed via Zerodha
  → Position appears in portfolio view
  → AI monitors and alerts on significant price moves
```

### Secondary Flow: Screener → Discovery → Analysis

```
User clicks AI Screener
  → Selects "Momentum" strategy (or types custom criteria)
  → AI returns ranked list of stocks matching criteria
  → User clicks a stock → detailed analysis panel
  → Adds to watchlist or places trade
```
