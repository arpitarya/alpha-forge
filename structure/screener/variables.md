# Screener — Variable Conventions

> Same Python rules as the backend / llm-gateway, with additions for the data-pipeline domain: dataframes, dates, model artefacts.

---

## 1. Carry-overs

Apply everything from `structure/backend/variables.md` (casing, type hints, async rules, errors). Below are the screener-specific additions.

---

## 2. Domain vocabulary

| Concept | Variable | Example |
|---------|----------|---------|
| Equity symbol (NSE ticker) | `symbol` (str, uppercase) | `"RELIANCE"`, `"INFY"` |
| Symbol with exchange suffix | `symbol_full` | `"RELIANCE.NS"` |
| Universe of symbols | `universe: list[str]` | `["RELIANCE", "INFY", ...]` |
| ISO calendar date | `scan_date: str` (always ISO) | `"2026-04-26"` |
| Datetime range | `start_date`, `end_date` | always `date` or ISO str — never naive datetime |
| OHLCV bar | `bar` / `bars: pd.DataFrame` | columns `open, high, low, close, volume` |
| Feature row | `features: pd.DataFrame` | one row per symbol per scan date |
| Model artefact | `model: lgb.Booster` | `model_type = "lightgbm"` |
| Model checkpoint path | `model_path: Path` | `data/models/2026-04-26_lgb.lgb` |
| Probability score | `probability: float` (0..1) | from `model.predict_proba(...)[:, 1]` |
| Rank within scan | `rank: int` (1-based) | 1 = best |
| Lookback window | `lookback_days: int` | 252 (≈ 1 trading year) |
| Forward window | `forward_days: int` | label horizon, e.g. 5 |

---

## 3. DataFrame conventions

### Column names

Always lowercase, snake_case, **no spaces**:

```python
ohlcv.columns = ["open", "high", "low", "close", "volume", "adj_close"]
features.columns = ["rsi_14", "macd_hist", "adx_14", "vol_sma_ratio", "dist_52w_high_pct"]
```

Feature names are **constants** in `models/feature_set.py`:

```python
class FeatureName(str, Enum):
    RSI_14            = "rsi_14"
    MACD_HIST         = "macd_hist"
    ADX_14            = "adx_14"
    VOL_SMA_RATIO     = "vol_sma_ratio"
    DIST_52W_HIGH_PCT = "dist_52w_high_pct"


FEATURES_USED: list[str] = [f.value for f in FeatureName]
```

This kills the entire class of "I renamed the column in one place but not the other" bugs.

### Indexing

- Time-series DataFrames are indexed by `pd.DatetimeIndex` named `date`.
- Multi-symbol features use a `MultiIndex(["symbol", "date"])` — never a flat column.

### Copy semantics

Every stage gets a fresh copy of its inputs:

```python
def compute_features(ohlcv: pd.DataFrame, config: FeatureConfig) -> pd.DataFrame:
    df = ohlcv.copy()    # never mutate the caller's frame
    ...
    return df
```

---

## 4. Date / time

```python
from datetime import date, datetime, timezone

scan_date: date = date(2026, 4, 26)
scan_date_iso: str = scan_date.isoformat()        # "2026-04-26"

# UTC always, named explicitly
generated_at = datetime.now(timezone.utc)
generated_at_iso = generated_at.isoformat()
```

Rules:
- `scan_date` is always ISO `YYYY-MM-DD`. No locale-formatted strings, ever.
- Datetimes are always tz-aware UTC. `datetime.utcnow()` is **forbidden** (deprecated + naive).
- File names use ISO date prefix: `2026-04-26_picks.json`, `2026-04-26_lgb.lgb`.

---

## 5. Reproducibility

```python
DEFAULT_RANDOM_STATE = 42

@dataclass(frozen=True)
class TrainConfig:
    random_state: int = DEFAULT_RANDOM_STATE
    n_splits: int = 5
    learning_rate: float = 0.05
    num_leaves: int = 63

train = lgb.train(params, dataset, num_boost_round=500, callbacks=[...], seed=config.random_state)
```

Anywhere RNG is used: pass the seed in. Don't call `np.random.seed(...)` globally — that mutates the world.

---

## 6. Numeric naming

```python
# Window sizes always carry _days / _periods / _bars suffix
lookback_days = 252
warmup_periods = 30
forward_horizon_days = 5

# Percentages always _pct
sharpe_threshold_pct = 0.0
max_drawdown_pct = -15.0

# Ratios — descriptive nouns, no suffix
vol_sma_ratio = volume / volume.rolling(20).mean()
hit_rate = wins / total
```

---

## 7. Pipeline reports

Every stage returns a `*Report` dataclass — never returns a bare value or DataFrame:

```python
@dataclass(frozen=True)
class StageReport:
    stage: str                          # "features"
    rows_in: int
    rows_out: int
    duration_ms: int
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PipelineReport:
    started_at: str
    finished_at: str
    stages: list[StageReport]
    pick_count: int
    output_path: Path
```

Reports serialise to JSON for run history (`data/runs/<date>.json`).

---

## 8. Path constants

`persistence/` owns the path scheme — stages and services import these constants instead of building paths inline:

```python
# persistence/paths.py
DATA_ROOT = Path("data")

OHLCV_DIR     = DATA_ROOT / "ohlcv"
FEATURES_DIR  = DATA_ROOT / "features"
MODELS_DIR    = DATA_ROOT / "models"
PICKS_DIR     = DATA_ROOT / "picks"
BACKTESTS_DIR = DATA_ROOT / "backtests"
RUNS_DIR      = DATA_ROOT / "runs"


def picks_path(scan_date: str, root: Path = PICKS_DIR) -> Path:
    return root / f"{scan_date}_picks.json"


def model_path(scan_date: str, model_type: str = "lgb", root: Path = MODELS_DIR) -> Path:
    return root / f"{scan_date}_{model_type}.lgb"
```

---

## 9. Model artefact naming

```python
model_type: str = "lightgbm"          # or "xgboost", "catboost"
model_short: str = "lgb"              # used in filenames
model_version: str = "v1"             # bump when feature set changes
checkpoint_path: Path = MODELS_DIR / f"{scan_date}_{model_short}_{model_version}.lgb"
```

When a model file is loaded, the filename is the source of truth for `(scan_date, model_type, version)` — don't read it from sidecar metadata first.

---

## 10. Logging

```python
logger.info("scan complete: date=%s picks=%d duration_ms=%d", scan_date, len(picks), elapsed_ms)
logger.warning("symbol=%s skipped: insufficient history (%d bars)", symbol, len(bars))
logger.exception("training failed for date=%s model=%s", scan_date, model_type)
```

Always include the scan date and the symbol in single-symbol failures so a run log is debuggable in isolation.

---

## 11. Notebook discipline

If a notebook cell defines a function or class, move it to `src/`. Cells should be:

```python
config = PipelineConfig(scan_date="2026-04-26", universe=NSE_500, lookback_days=252)
report = ScreenerPipeline(config).run_full()
report.summary()
```

A notebook should read top-to-bottom as a script the user could paste into a CLI.

---

## 12. Quick reference card (screener-specific)

```
Symbol               UPPER snake               "RELIANCE", "INFY"
Universe             list[str]                 NSE_500
Date                 ISO YYYY-MM-DD            "2026-04-26"
Datetime             UTC tz-aware              datetime.now(timezone.utc)
DataFrame columns    snake_case                rsi_14, macd_hist
DataFrame index      MultiIndex(symbol, date)
Probability          0..1 float                pick.probability
Rank                 1-based int               pick.rank
Window suffix        _days / _periods / _bars  lookback_days=252
Percentage suffix    _pct                      max_drawdown_pct
Random state         passed via *Config        DEFAULT_RANDOM_STATE = 42
Filenames            <date>_<short>.<ext>      2026-04-26_lgb.lgb
Path constants       persistence/paths.py      PICKS_DIR, picks_path(date)
Stage signature      run(in, out, *, config)   returns StageReport
```
