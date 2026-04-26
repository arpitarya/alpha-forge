# Screener — Application Structure

> **Core principle**: a deterministic offline ML pipeline that produces a ranked list of NSE picks per scan date, plus a backend service that serves them to the terminal UI. Notebook-first development; CLI-second; web routes consume saved artefacts.
> Soft caps: 200 lines per pipeline stage · 300 lines per service module.

---

## What this module is

The screener has two halves:

1. **Offline pipeline** (`screener/`) — Jupyter notebook + Python package that ingests OHLCV data, engineers features, trains LightGBM, backtests, and emits per-scan-date pick files.
2. **Backend service** (`backend/app/services/screener.py` + `backend/app/routes/screener.py`) — reads the saved artefacts and exposes them via REST.

Both halves share the same `Pick` schema so a notebook-generated CSV is byte-identical to one written by the daily scan script.

---

## Directory layout

```
screener/
├── pyproject.toml                       packaged as alphaforge-screener (planned)
├── README.md
├── PLAN.md                              roadmap
├── implement.txt
├── notebooks/
│   ├── screener_pipeline.ipynb          end-to-end (data → features → train → backtest → scan)
│   └── feature_exploration.ipynb        ad-hoc feature engineering
├── src/alphaforge_screener/
│   ├── __init__.py                      barrel: ScreenerPipeline, Pick, FeatureSet
│   ├── pipeline.py                      orchestrator — chains the stages
│   ├── stages/
│   │   ├── ingest.py                    OHLCV download + cache
│   │   ├── features.py                  RSI, MACD, ADX, vol ratio, dist-from-52w
│   │   ├── train.py                     LightGBM training + checkpoints
│   │   ├── backtest.py                  walk-forward validation
│   │   └── scan.py                      live scan → ranked picks
│   ├── models/
│   │   ├── pick.py                      Pydantic Pick model
│   │   ├── feature_set.py
│   │   └── scan_result.py
│   ├── persistence/
│   │   ├── picks_writer.py              JSON writer for data/picks/<date>_picks.json
│   │   ├── picks_reader.py              JSON reader (used by backend)
│   │   └── model_store.py               LightGBM model checkpoints
│   ├── cli.py                           CLI: pipeline, scan, backfill
│   └── utils/
│       ├── nse_universe.py              symbol list (NSE 500, etc.)
│       └── trading_calendar.py          NSE holidays
├── tests/
│   ├── fixtures/
│   │   ├── ohlcv/                       small sample OHLCV CSVs
│   │   └── picks/                       golden pick files
│   ├── test_features.py                 deterministic feature math
│   ├── test_pipeline.py                 end-to-end on fixture data
│   ├── test_picks_writer.py
│   └── test_picks_reader.py
├── data/                                gitignored
│   ├── ohlcv/                           cached price history
│   ├── features/                        engineered feature parquets
│   ├── models/                          trained .lgb checkpoints
│   ├── picks/                           daily picks JSON
│   └── backtests/                       backtest reports
└── docs/
    └── PIPELINE.md                      stage-by-stage walkthrough

# On the backend side (consumer)
backend/
└── app/
    ├── services/
    │   └── screener.py                  ScreenerService — reads from screener/data/picks
    └── routes/
        └── screener.py                  GET /screener/picks, /dates · POST /picks
```

---

## Pipeline architecture

```
NSE OHLCV (yfinance, etc.)
        │
        ▼
┌──────────────────┐
│  ingest          │  cache to data/ohlcv/<symbol>.parquet
└────────┬─────────┘
         ▼
┌──────────────────┐
│  features        │  RSI, MACD, ADX, vol ratio, 52w-distance, …
└────────┬─────────┘   → data/features/<date>.parquet
         ▼
┌──────────────────┐
│  train           │  LightGBM, walk-forward CV
└────────┬─────────┘   → data/models/<date>_<algo>.lgb
         ▼
┌──────────────────┐
│  backtest        │  rolling window, sharpe / hit-rate / drawdown
└────────┬─────────┘   → data/backtests/<date>.json
         ▼
┌──────────────────┐
│  scan            │  produce today's ranked picks
└────────┬─────────┘   → data/picks/<date>_picks.json
         ▼
   POST /screener/picks  (optional — embed into vector store)
         ▼
   GET  /screener/picks  → terminal UI
```

Each stage is a free function with the same shape:

```python
def run(input_path: Path, output_path: Path, *, config: StageConfig) -> StageReport: ...
```

The pipeline orchestrator wires them together; CLI / notebook can call any single stage in isolation.

---

## Module responsibilities

### `pipeline.py`

The orchestrator. Takes a `PipelineConfig`, runs the stages in order, persists artefacts, returns a `PipelineReport`.

```python
class ScreenerPipeline:
    def __init__(self, config: PipelineConfig) -> None: ...

    async def run_full(self) -> PipelineReport: ...
    async def run_scan_only(self) -> ScanResult: ...
    async def run_backfill(self, start: date, end: date) -> list[ScanResult]: ...
```

### `stages/`

One module per stage. Each stage:
- Reads from the previous stage's output path.
- Writes to a versioned output path.
- Returns a `StageReport` with `rows_in`, `rows_out`, `duration_ms`, `warnings`.

```python
# stages/features.py
@dataclass(frozen=True)
class FeatureConfig:
    universe: list[str]
    lookback_days: int = 252
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26


def compute_features(ohlcv: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame: ...
```

Stages are **pure** — no global state, no implicit configuration. Anything that varies between runs is in the `*Config` dataclass.

### `models/`

Pydantic / dataclass schemas shared between offline and backend. Since the backend depends on the **shape** of `Pick`, this module is the contract.

```python
class Pick(BaseModel):
    symbol: str                        # "RELIANCE"
    probability: float                 # 0..1
    rank: int
    rsi_14: float | None = None
    macd_hist: float | None = None
    adx_14: float | None = None
    vol_sma_ratio: float | None = None
    dist_52w_high_pct: float | None = None


class ScanResult(BaseModel):
    scan_date: str                     # YYYY-MM-DD
    model_type: str
    picks: list[Pick]
    metadata: dict[str, str] = {}
```

### `persistence/`

Owns all on-disk I/O. Keeps the file path scheme (`data/picks/<date>_picks.json`) in one place so stages don't hardcode it.

```python
class PicksWriter:
    def write(self, scan_result: ScanResult, root: Path = PICKS_DIR) -> Path: ...


class PicksReader:
    def read(self, scan_date: str | None = None, root: Path = PICKS_DIR) -> ScanResult: ...
    def list_dates(self, root: Path = PICKS_DIR) -> list[str]: ...
```

The backend's `ScreenerService` is essentially a thin wrapper around `PicksReader`.

### `cli.py`

```bash
alphaforge-screener pipeline   --start 2026-01-01 --end 2026-04-26
alphaforge-screener scan       --date today
alphaforge-screener backfill   --start 2024-01-01 --end 2024-12-31
alphaforge-screener push       --date 2026-04-26   # POST to backend
```

---

## Backend integration

The backend consumes the screener through a tiny service layer:

```python
# backend/app/services/screener.py
class ScreenerService:
    def __init__(self) -> None:
        self._reader = PicksReader()

    async def save_picks(self, scan_date: str, model_type: str, picks: list[dict]) -> dict: ...
    async def get_picks(self, scan_date: str | None = None) -> dict: ...
    async def list_scan_dates(self) -> list[str]: ...
```

Routes (`backend/app/routes/screener.py`):

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/screener/picks?date=YYYY-MM-DD` | Read picks for a date (latest if omitted). |
| `GET`  | `/screener/dates` | List all scan dates with picks on disk. |
| `POST` | `/screener/picks` | Push picks from notebook/CLI; triggers vector embedding in background. |
| `POST` | `/screener/picks/embed-backfill` | Re-embed existing picks JSON. |

Frontend hits `/screener/picks` from the terminal `<ScreenerPanel/>`.

---

## Cross-cutting conventions

### Reproducibility

- Every stage takes a `*Config` and writes a `*Report`. Reports are JSON-serializable so a run can be reconstructed.
- Random seeds: every model training step accepts `random_state` in its config; default `42`.
- Date stamps in filenames are ISO `YYYY-MM-DD` — never locale-formatted.

### No paid data

`ingest.py` only uses free sources (yfinance for OHLCV, NSE bhav copies for indices). If a paid feed is added later it goes behind a flag in `IngestConfig`.

### Disclaimer

Every payload from the backend that returns picks **must** carry the disclaimer (asserted in tests):

> Not SEBI registered investment advice.

### Notebook ↔ package parity

Every cell in `notebooks/screener_pipeline.ipynb` is a one-liner that calls into the package — no business logic in the notebook. If you find yourself writing `def …` in a cell, move it into `src/`.

---

## Testing

```
tests/
├── fixtures/
│   ├── ohlcv/                # 30-day OHLCV per symbol — tiny but real
│   └── picks/                # golden Pick JSON for regression
├── test_features.py          # deterministic math against known inputs
├── test_pipeline.py          # end-to-end on fixtures
├── test_picks_writer.py
└── test_picks_reader.py
```

Rules:
- Feature math is deterministic — assert exact values, not ranges.
- Pipeline tests use the smallest possible fixture set (≤ 5 symbols × 30 days).
- Backtest tests use a fixed random seed and assert key metrics within ε.

---

## Anti-patterns

- ❌ Hard-coded paths inside stages — go through `persistence/`.
- ❌ Mutable `pd.DataFrame` operations across stages — each stage gets its own copy.
- ❌ "Magic" feature names — column names are constants in `models/feature_set.py`.
- ❌ `np.random` calls without `random_state`. Reproducibility or it's not real.
- ❌ Notebook code that defines functions or classes — those belong in `src/`.
