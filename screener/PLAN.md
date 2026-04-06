# Screener: Weekly Stock Return Prediction Algorithm

> **Disclaimer: This is NOT SEBI registered investment advice. For personal research and educational use only. Past performance does not guarantee future results.**

## TL;DR

Build a standalone Python screener that scans **all NSE-listed stocks (~2000+)**, computes technical + fundamental features, trains a **LightGBM classifier** to predict which stocks will return **>5% in the next 5 trading days**, and includes a **backtesting framework** to validate before going live. Uses only **free data sources** (yfinance, nselib, jugaad-data). Standalone first, integrate into AlphaForge later.

**Recommended approach**: Hybrid (Technical indicators as ML features in LightGBM). Technical-only rules as a comparison baseline.

### Why Hybrid?

- **Pure rules** are too rigid across 2000+ stocks — static RSI/MACD thresholds can't adapt to different regimes.
- **Pure ML** without domain features overfits on noise — the model needs structured financial signal inputs.
- **Fundamentals alone** move too slowly for a 1-week prediction horizon.
- **Hybrid** uses domain-expert technical indicators as features in a gradient boosted tree — best signal-to-noise ratio.
- **LightGBM** over XGBoost: faster training, native categorical support, better with imbalanced classes (most stocks don't return >5%/week).

---

## Data Sources (All Free)

| Source | What It Provides | Python Package |
|--------|-----------------|----------------|
| **Yahoo Finance** | 2yr+ daily OHLCV for all NSE stocks (`.NS` suffix), index data, basic fundamentals (PE, PB, market cap) | `yfinance` |
| **NSE India (via nselib)** | Full equity list, delivery % data, bulk/block deals, FII/DII activity, bhav copy | `nselib` |
| **NSE India (via jugaad-data)** | Backup source for historical stock/index data, bhavcopy downloads | `jugaad-data` |

### Data Limitations

- **yfinance**: Rate-limited (batch 500 tickers max), may miss delisted stocks (survivorship bias), Adjusted Close handles splits/dividends.
- **nselib**: Uses NSE website scraping — can be blocked if too aggressive. Add `sleep(0.5)` between calls. Date format: `dd-mm-yyyy`.
- **jugaad-data**: Fallback for when yfinance/nselib fail. Good for bhavcopy and index data.

---

## Phase 1: Data Pipeline

**Directory**: `screener/data/`

### Step 1.1 — Stock Universe Fetcher (`fetch_universe.py`)

- Fetch all NSE-listed equities via `nselib.capital_market.equity_list()`
- Filter: keep only `series == "EQ"` (exclude BE/BZ/SM/BL series)
- Map to yfinance format: `{SYMBOL}.NS` (e.g., `RELIANCE.NS`)
- Volume filter: exclude stocks with avg daily volume < 10,000 over 90 days
- Output: `data/raw/universe.csv` + `data/raw/universe_filtered.csv`
- Expected: ~2000+ total → ~1200-1500 after volume filter

### Step 1.2 — Historical OHLCV Download (`fetch_ohlcv.py`)

- Download 2 years of daily OHLCV for all filtered stocks
- Use `yfinance.download()` in batch mode (500 tickers per batch)
- Store as individual Parquet files: `data/raw/ohlcv/{SYMBOL}.parquet`
- Columns: Open, High, Low, Close, Adj Close, Volume
- Supports incremental update mode (append new data to existing files)

### Step 1.3 — Supplementary NSE Data (`fetch_nse_data.py`)

- **Delivery %**: `nselib.capital_market.price_volume_and_deliverable_position_data()` — high delivery % signals institutional conviction
- **Bulk deals**: `nselib.capital_market.bulk_deal_data()` — large institutional transactions
- **Block deals**: `nselib.capital_market.block_deals_data()` — negotiated large deals
- **FII/DII activity**: `nselib.capital_market.fii_dii_trading_activity()` — market-wide institutional flows

### Step 1.4 — Index Benchmarks (`fetch_nse_data.py`)

- Download via yfinance: NIFTY 50 (`^NSEI`), SENSEX (`^BSESN`), BANK NIFTY (`^NSEBANK`), NIFTY IT (`^CNXIT`)
- Required for Phase 2 relative strength features
- Store as: `data/raw/indices/{INDEX_NAME}.parquet`

---

## Phase 2: Feature Engineering

**Directory**: `screener/features/`  
**~40-50 features** computed per stock per day.

### 2.1 — Technical Indicators (`technical.py`)

Uses `ta` library (pure Python, no C dependency — unlike `ta-lib`).

| Feature Group | Indicators | Rationale |
|---|---|---|
| **Momentum** | RSI(14), RSI(7), Stochastic %K/%D, Williams %R, ROC(5,10,20) | Overbought/oversold, momentum strength |
| **Trend** | MACD line/signal/histogram, ADX(14), Aroon Up/Down, SMA(20/50/200) cross signals | Trend direction & strength |
| **Volatility** | Bollinger %B, Bollinger Bandwidth, ATR(14), Keltner Channel position | Squeeze/breakout detection |
| **Volume** | OBV, Volume SMA ratio (vol/vol_20d), VWAP, Accumulation/Distribution, MFI | Smart money detection |
| **Price Action** | Distance from 52w high/low (%), consecutive up/down days, gap up/down %, candle body ratio | Pattern recognition |

### 2.2 — Relative Strength (`relative_strength.py`)

- Stock return vs NIFTY 50 return over 5, 10, 20 days
- Stock return vs sector index return (sector-relative performance)
- Rank within sector by momentum

### 2.3 — Fundamental Features (`fundamental.py`)

- PE ratio, PB ratio, Market cap category (large/mid/small/micro)
- 52-week return, Beta
- Cached weekly (these update infrequently)

### 2.4 — NSE-Specific Features (`nse_features.py`)

- Delivery % — high delivery % signals institutional conviction
- Bulk/block deal presence in last N days — binary flag
- FII/DII net buy/sell — market-wide regime indicator

### 2.5 — Derived / Interaction Features (`build_features.py`)

- `RSI_14 × Volume_ratio` — momentum + volume confirmation
- `Distance_from_52w_high × ADX` — breakout + trend strength
- `Bollinger_%B` when bandwidth is narrowing — squeeze about to pop

---

## Phase 3: Labeling & Dataset Construction

**Directory**: `screener/dataset/`

### Target Variable (`labeler.py`)

- **Classification**: Did the stock return >5% in the next 5 trading days? (binary: 1/0)
- **Regression**: Actual 5-day forward return (for ranking)
- Uses **Adjusted Close** to handle splits/dividends
- Last 5 rows per stock excluded (no future data available)

### Dataset Assembly (`build_dataset.py`)

- One row per stock-day: all features + target label
- ~200k+ rows (2000 stocks × ~500 trading days)
- Additional columns: symbol, date, sector, market_cap_category

### Data Quality Rules

- Drop rows with >30% NaN features (indicator warmup period)
- **No lookahead bias**: all features computed using only data available up to that day
- Survivorship bias acknowledged as limitation with free data sources

---

## Phase 4: Model Training

**Directory**: `screener/models/`

### 4.1 — Baseline: Technical Rules Strategy (`baseline_rules.py`)

Simple rule-based screener for comparison:
- RSI(14) < 35 AND crossing back above 30 (oversold bounce)
- Volume > 2× 20-day average (volume surge)
- MACD histogram turning positive
- Price above SMA(50)

### 4.2 — Primary: LightGBM Classifier (`train_lightgbm.py`)

- Input: all ~40-50 features
- Output: probability of >5% return in 5 days
- Why: faster training, native categorical support, handles imbalanced data well
- Key hyperparameters: `num_leaves`, `learning_rate`, `min_child_samples`, `subsample`, `colsample_bytree`, `scale_pos_weight`

### 4.3 — Comparison: XGBoost Classifier (`train_xgboost.py`)

- Same features/labels, different model for comparison
- `XGBClassifier` with similar hyperparameters

### 4.4 — Walk-Forward Cross-Validation (`walk_forward.py`) ⚠️ CRITICAL

**Never use random train/test split for time series** — causes lookahead bias.

```
Fold 1:  Train [Month 1–12]  → Test [Month 13]
Fold 2:  Train [Month 1–13]  → Test [Month 14]
Fold 3:  Train [Month 1–14]  → Test [Month 15]
...
Fold N:  Train [Month 1–(N+11)] → Test [Month N+12]
```

- Expanding window (preferred over sliding)
- Minimum 12 months training, 1 month test per fold
- Simulates real-world usage: always train on past, predict future

### 4.5 — Feature Importance & Selection

- LightGBM feature importance (gain-based)
- SHAP values for interpretability
- Drop near-zero importance features to reduce overfitting

---

## Phase 5: Backtesting Framework

**Directory**: `screener/backtest/`

### 5.1 — Backtest Engine (`engine.py`)

- For each test period in walk-forward CV:
  - Model outputs top N stocks ranked by predicted probability
  - Simulate: buy at next day's open, sell after 5 trading days at close
  - Track: entry price, exit price, return per trade, hit rate
- Configuration: top N = 5, 10, 20 picks per week

### 5.2 — Realistic Cost Model (Indian Market Specific)

| Cost | Rate | Applied On |
|------|------|-----------|
| Brokerage | ₹20/order or 0.03% | Both sides |
| STT | 0.1% | Sell side (delivery) |
| Exchange txn | 0.00345% | Both sides |
| GST | 18% | On brokerage + txn charges |
| Stamp duty | 0.015% | Buy side |
| **Total round-trip** | **~0.25-0.30%** | |

### 5.3 — Performance Metrics (`metrics.py`)

| Metric | Target |
|---|---|
| Hit Rate (profitable / total trades) | >55% |
| Avg Win (mean return of winners) | >5% |
| Avg Loss (mean return of losers) | <3% |
| Profit Factor (gross profit / gross loss) | >1.5 |
| Sharpe Ratio (annualized) | >1.5 |
| Max Drawdown | <20% |
| CAGR | >25% |
| Win/Loss Ratio | >1.5 |

### 5.4 — Comparison Report (`report.py`)

- Side-by-side: Technical Rules vs LightGBM vs XGBoost
- Per-model: all metrics above + equity curve plot
- Output: `reports/backtest_report.html` or Jupyter notebook

---

## Phase 6: Live Screener

**Directory**: `screener/live/`

### 6.1 — Daily Scan Script (`scan.py`)

Run after market close (~3:45 PM IST):

1. Fetch latest OHLCV for all stocks
2. Compute features for most recent day
3. Load trained model (`saved/` directory)
4. Predict probability for all stocks
5. Rank and output top 20 with confidence scores

Output: `picks/{date}_weekly_picks.csv`

### 6.2 — Signal Explanation (`explain.py`)

For each pick, show contributing features via SHAP:

> "RELIANCE: RSI oversold bounce (RSI=28→35), volume surge 3.2×, MACD bullish crossover"

### 6.3 — Retraining Schedule

- Retrain monthly with expanding window
- Track model drift: alert if live hit rate drops >10% below backtest rate

---

## Project Structure

```
screener/
├── PLAN.md                       # This file
├── README.md                     # Usage docs + disclaimer
├── requirements.txt              # Python dependencies
├── config.py                     # Paths, thresholds, index symbols
├── __init__.py
├── data/
│   ├── __init__.py
│   ├── fetch_universe.py         # Step 1.1 — NSE equity list
│   ├── fetch_ohlcv.py            # Step 1.2 — yfinance OHLCV download
│   ├── fetch_nse_data.py         # Step 1.3 + 1.4 — delivery %, deals, indices
│   └── raw/                      # Downloaded data (gitignored)
│       ├── universe.csv
│       ├── universe_filtered.csv
│       ├── ohlcv/                # Per-symbol Parquet files
│       ├── indices/              # Index Parquet files
│       └── nse_supplementary/    # Delivery %, deals, FII/DII
├── features/
│   ├── __init__.py
│   ├── technical.py              # Technical indicators (ta library)
│   ├── relative_strength.py      # vs index/sector returns
│   ├── fundamental.py            # PE, PB, market cap
│   ├── nse_features.py           # Delivery %, deal flags
│   └── build_features.py         # Orchestrator — combines all features
├── dataset/
│   ├── __init__.py
│   ├── labeler.py                # Target: >5% in 5 days
│   └── build_dataset.py          # Final dataset assembly + quality checks
├── models/
│   ├── __init__.py
│   ├── baseline_rules.py         # Rule-based strategy
│   ├── train_lightgbm.py         # LightGBM classifier
│   ├── train_xgboost.py          # XGBoost classifier
│   ├── walk_forward.py           # Walk-forward CV engine
│   └── saved/                    # Serialized models (gitignored)
├── backtest/
│   ├── __init__.py
│   ├── engine.py                 # Simulator with cost model
│   ├── metrics.py                # Performance metrics
│   └── report.py                 # HTML/notebook comparison report
├── live/
│   ├── __init__.py
│   ├── scan.py                   # Daily scanner
│   ├── explain.py                # SHAP-based signal explanation
│   └── picks/                    # Daily output CSVs (gitignored)
├── reports/                      # Backtest reports (gitignored)
└── notebooks/
    ├── 01_data_exploration.ipynb
    ├── 02_feature_analysis.ipynb
    └── 03_backtest_results.ipynb
```

---

## Integration with AlphaForge (Future)

Once the standalone screener is validated, integrate into the existing backend:

| Existing File | Action |
|---|---|
| `backend/app/services/ai_service.py` → `run_screener()` | Wire to screener model |
| `backend/app/routes/ai.py` → `/screener` endpoint | Return top picks as JSON |
| `frontend/src/lib/queries.ts` → `useScreener()` hook | Already wired up |
| `backend/app/services/market_data.py` | Share data pipeline |

---

## Verification Checklist

- [ ] `fetch_universe.py` → ~2000+ symbols fetched
- [ ] `fetch_ohlcv.py` on 50 stocks → OHLCV shape correct, no NaN in Close
- [ ] RSI/MACD values match TradingView for RELIANCE.NS
- [ ] No lookahead bias: feature dates ≤ row date, target dates > row date
- [ ] Walk-forward CV: train dates < test dates in every fold
- [ ] Backtest hit rate significantly beats random baseline (~15-20%)
- [ ] Live scan output: 20 picks with valid probability scores

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Standalone vs integrated | Standalone first | Faster iteration, no backend coupling |
| Data source | Free only (yfinance, nselib) | No budget constraint |
| Technical library | `ta` over `ta-lib` | Pure Python, no C compilation hassle |
| Primary model | LightGBM | Fast, handles imbalance, native categoricals |
| Return threshold | >5% / 5 days | Realistic for Indian small/mid-cap weekly swings |
| Task type | Classification | "Will it beat 5%?" > "exact return" |
| CV strategy | Walk-forward | Mandatory for time series (no lookahead) |
| Storage format | Parquet | Faster reads, columnar compression |

---

## Disclaimers

- **Not SEBI registered investment advice** — all outputs must carry this disclaimer
- Past performance does not guarantee future results
- Markets are inherently unpredictable; any model can fail during black swan events
- Risk management (position sizing, stop-losses) is essential — planned for a future iteration
- Survivorship bias is a known limitation with free data sources
- This tool assists decision-making; the user is responsible for all trading decisions
