# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
# ---

# %% [markdown]
# # AlphaForge Screener — Interactive Pipeline
#
# > **Disclaimer: This is NOT SEBI registered investment advice. For personal research and educational use only. Past performance does not guarantee future results.**
#
# This notebook provides an interactive interface to run and test the complete screener pipeline:
#
# | Phase | Module | Description |
# |-------|--------|-------------|
# | 1 | Data Pipeline | Fetch universe, OHLCV, NSE supplementary data |
# | 2 | Feature Engineering | Technical, relative strength, fundamental, NSE features |
# | 3 | Labeling & Dataset | Forward returns, classification labels, quality filters |
# | 4 | Model Training | LightGBM, XGBoost, baseline rules, walk-forward CV |
# | 5 | Backtesting | Cost-aware backtest with Indian market costs |
# | 6 | Live Scanning | Predict & rank today's picks with explanations |
# | 7 | AlphaForge Integration | Push results to the backend API |

# %% [markdown]
# ## Setup & Imports

# %%
import sys
from pathlib import Path

# Ensure the repo root is on sys.path so `screener.*` imports work
REPO_ROOT = Path.cwd().resolve()
while REPO_ROOT.name and not (REPO_ROOT / "screener" / "config.py").exists():
    REPO_ROOT = REPO_ROOT.parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

print(f"Repo root: {REPO_ROOT}")
print(f"Python:    {sys.version}")

# %%
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", 80)
pd.set_option("display.max_rows", 60)
pd.set_option("display.float_format", "{:.4f}".format)

from screener import config
print(f"Base dir:   {config.BASE_DIR}")
print(f"Data dir:   {config.DATA_DIR}")
print(f"Models dir: {config.MODELS_DIR}")

# %% [markdown]
# ---
# ## Phase 1 — Data Pipeline
#
# Fetch the stock universe, historical OHLCV, index benchmarks, and NSE supplementary data.

# %% [markdown]
# ### 1.1 — Fetch & Filter Stock Universe

# %%
from screener.data.fetch_universe import fetch_universe

full_universe, filtered_universe = fetch_universe(skip_volume_filter=False)

print(f"Full universe:     {len(full_universe)} stocks")
print(f"Filtered universe: {len(filtered_universe)} stocks (vol > {config.MIN_AVG_VOLUME_90D:,}/day)")
print()
filtered_universe.head(10)

# %% [markdown]
# ### 1.2 — Download Historical OHLCV

# %%
from screener.data.fetch_ohlcv import fetch_ohlcv

# Set incremental=True to only download new data (fast update)
# Set incremental=False for a full re-download
result = fetch_ohlcv(incremental=True)

print(f"Total symbols: {result['total']}")
print(f"Success:       {result['success']}")
print(f"Failed:        {result['failed']}")

# %% [markdown]
# ### 1.3 — Fetch NSE Supplementary Data & Index Benchmarks

# %%
from screener.data.fetch_nse_data import fetch_all_nse_supplementary, fetch_index_data

# Index benchmarks (NIFTY 50, SENSEX, BANK NIFTY, NIFTY IT)
indices = fetch_index_data()
for name, df in indices.items():
    print(f"{name}: {len(df)} days, {df.index.min().date()} → {df.index.max().date()}")

print()

# NSE supplementary (delivery %, bulk/block deals)
nse_data = fetch_all_nse_supplementary(days_back=30)
for key, val in nse_data.items():
    print(f"{key}: {len(val) if val is not None else 'N/A'} rows")

# %% [markdown]
# ### 1.4 — Quick Data Health Check

# %%
ohlcv_files = list(config.OHLCV_DIR.glob("*.parquet"))
print(f"OHLCV files on disk: {len(ohlcv_files)}")

# Spot-check a random stock
if ohlcv_files:
    sample = pd.read_parquet(ohlcv_files[0])
    sym = ohlcv_files[0].stem
    print(f"\nSample — {sym}: {len(sample)} days, "
          f"{sample.index.min().date()} → {sample.index.max().date()}")
    print(f"Columns: {list(sample.columns)}")
    sample.tail(5)

# %% [markdown]
# ---
# ## Phase 2 — Feature Engineering
#
# Compute ~59 features per stock per day: technical indicators, relative strength, fundamentals, NSE-specific, and interaction features.

# %% [markdown]
# ### 2.1 — Build Features for a Single Stock

# %%
from screener.features.build_features import build_features_for_symbol

# Pick a well-known stock to inspect features
SAMPLE_SYMBOL = "RELIANCE.NS"

features_df = build_features_for_symbol(
    SAMPLE_SYMBOL,
    include_fundamentals=True,
    include_nse=True,
)

if features_df is not None:
    print(f"Features for {SAMPLE_SYMBOL}: {features_df.shape[0]} rows × {features_df.shape[1]} cols")
    print(f"\nFeature columns ({len(features_df.columns)}):")
    for i, col in enumerate(features_df.columns, 1):
        print(f"  {i:2d}. {col}")
    print()
    features_df.tail(5)
else:
    print(f"No data for {SAMPLE_SYMBOL}")

# %% [markdown]
# ### 2.2 — Feature Statistics Overview

# %%
if features_df is not None:
    # NaN coverage per feature
    nan_pct = features_df.isna().mean().sort_values(ascending=False)
    print("NaN % per feature (top 15):")
    print(nan_pct.head(15).to_string(float_format="{:.1%}".format))
    print(f"\nFeatures with >50% NaN: {(nan_pct > 0.5).sum()}")
    print(f"Features with zero NaN: {(nan_pct == 0).sum()}")
    print()
    features_df.describe().T

# %% [markdown]
# ---
# ## Phase 3 — Labeling & Dataset
#
# Label each row with forward 5-day return and a binary target (>5% = positive).

# %% [markdown]
# ### 3.1 — Build Full Dataset
#
# Set `max_symbols=None` for the full universe (takes 10–30 min), or limit for quick testing.

# %%
from screener.dataset.build_dataset import build_dataset

# Quick test: limit to 10 symbols; set max_symbols=None for full run
MAX_SYMBOLS = 10

dataset = build_dataset(
    max_symbols=MAX_SYMBOLS,
    include_fundamentals=True,
    include_nse=True,
    save=True,
)

print(f"Dataset shape: {dataset.shape}")
print(f"Symbols:       {dataset['SYMBOL'].nunique()}")
print(f"Date range:    {dataset.index.min().date()} → {dataset.index.max().date()}")
dataset.head(5)

# %% [markdown]
# ### 3.2 — Class Distribution

# %%
target_col = "TARGET_5PCT_5D"
if target_col in dataset.columns:
    dist = dataset[target_col].value_counts(dropna=False).sort_index()
    total = len(dataset)
    print("Target Distribution:")
    for val, count in dist.items():
        label = {0: "Negative (≤5%)", 1: "Positive (>5%)"}.get(val, f"NaN")
        print(f"  {label}: {count:,} ({count/total:.1%})")
    print(f"\nImbalance ratio (neg/pos): "
          f"{dist.get(0, 0) / max(dist.get(1, 1), 1):.1f}:1")

# %% [markdown]
# ---
# ## Phase 4 — Model Training
#
# Train LightGBM and XGBoost classifiers using walk-forward cross-validation.

# %% [markdown]
# ### 4.0 — Load Dataset (if already saved)

# %%
from screener.dataset.build_dataset import build_dataset

dataset_path = config.DATASET_DIR / "output" / "dataset.parquet"
if dataset_path.exists():
    dataset = pd.read_parquet(dataset_path)
    print(f"Loaded dataset: {dataset.shape[0]:,} rows × {dataset.shape[1]} cols")
    print(f"Symbols: {dataset['SYMBOL'].nunique()}, "
          f"Date range: {dataset.index.min().date()} → {dataset.index.max().date()}")
else:
    print("No saved dataset found — run Phase 3 first.")

# %% [markdown]
# ### 4.1 — Baseline Rules

# %%
from screener.models.baseline_rules import evaluate_baseline

for strategy in ["strict", "relaxed", "momentum"]:
    result = evaluate_baseline(dataset, strategy=strategy)
    print(f"\n{'='*50}")
    print(f"Baseline — {strategy.upper()}")
    print(f"{'='*50}")
    print(f"  Signals:       {result['n_signals']:,}")
    print(f"  Hit rate:      {result['hit_rate']:.1%}")
    print(f"  Avg return:    {result['avg_return']:.2%}")
    print(f"  Profit factor: {result['profit_factor']:.2f}")

# %% [markdown]
# ### 4.2 — Train LightGBM

# %%
from screener.models.train_lightgbm import train_lightgbm

# Identify feature columns (exclude metadata and labels)
EXCLUDE_COLS = {"SYMBOL", "SECTOR", "MARKET_CAP_CATEGORY",
                "FORWARD_RETURN_5D", "TARGET_5PCT_5D", "Adj Close"}
feature_cols = [c for c in dataset.columns if c not in EXCLUDE_COLS]

lgb_result = train_lightgbm(
    dataset,
    feature_cols=feature_cols,
    min_train_months=12,
    test_months=1,
    prob_threshold=0.5,
    save=True,
)

print("\nLightGBM Aggregate Metrics:")
for k, v in lgb_result["agg_metrics"].items():
    if isinstance(v, float):
        print(f"  {k}: {v:.4f}")
    else:
        print(f"  {k}: {v}")

# %% [markdown]
# ### 4.3 — Train XGBoost

# %%
from screener.models.train_xgboost import train_xgboost

xgb_result = train_xgboost(
    dataset,
    feature_cols=feature_cols,
    min_train_months=12,
    test_months=1,
    prob_threshold=0.5,
    save=True,
)

print("\nXGBoost Aggregate Metrics:")
for k, v in xgb_result["agg_metrics"].items():
    if isinstance(v, float):
        print(f"  {k}: {v:.4f}")
    else:
        print(f"  {k}: {v}")

# %% [markdown]
# ### 4.4 — Feature Importance Comparison

# %%
from screener.models.feature_importance import compare_model_importances, generate_report

importance_df = compare_model_importances()
print("Top 20 Features (by LightGBM importance):")
importance_df.head(20)

# %% [markdown]
# ---
# ## Phase 5 — Backtesting
#
# Run a realistic backtest with Indian market transaction costs (STT, brokerage, GST, stamp duty).

# %%
from screener.backtest.engine import BacktestEngine, CostModel
from screener.backtest.metrics import compute_all_metrics, format_metrics_table, check_benchmarks
from screener.backtest.report import generate_text_report

# Build predictions dict from walk-forward folds
def build_predictions_from_result(result):
    """Extract fold predictions for BacktestEngine."""
    predictions = {}
    fold_indices = {}
    for fr in result["fold_results"]:
        fid = fr.fold_id
        predictions[fid] = (fr.predictions, fr.probabilities)
        # Reconstruct test indices from fold metadata
        test_mask = (
            (dataset.index >= fr.test_start) & (dataset.index <= fr.test_end)
        )
        fold_indices[fid] = np.where(test_mask)[0]
    return predictions, fold_indices


# Backtest LightGBM
engine = BacktestEngine(
    top_n=10,
    initial_capital=1_000_000,
    cost_model=CostModel(),
)

lgb_preds, lgb_indices = build_predictions_from_result(lgb_result)
trades, equity_curve, bt_metrics = engine.run_from_predictions(
    dataset, lgb_preds, lgb_indices,
)

print(f"Trades: {len(trades)}")
print(format_metrics_table(bt_metrics, title="LightGBM Backtest"))

# %% [markdown]
# ### 5.1 — Benchmark Check

# %%
benchmarks = check_benchmarks(bt_metrics)
print("Benchmark Check:")
for metric, info in benchmarks.items():
    status = "PASS" if info["passed"] else "FAIL"
    print(f"  [{status}] {metric}: {info['actual']:.4f} (target: {info['target']})")

# %% [markdown]
# ---
# ## Phase 6 — Live Scanning
#
# Run the model against today's data to generate weekly stock picks.

# %%
from screener.live.scan import (
    get_available_symbols,
    compute_features_latest,
    load_model,
    predict_and_rank,
)

# Load trained model
model, meta = load_model(model_type="lightgbm")
print(f"Model loaded: {meta['model_type']}, trained {meta['trained_at']}")
print(f"Features: {meta['n_features']}, AUC-ROC: {meta['agg_metrics'].get('auc_roc', 'N/A'):.4f}")

# Compute latest features for available stocks
symbols = get_available_symbols()
print(f"\nScanning {len(symbols)} stocks...")

latest_features = compute_features_latest(
    symbols,
    include_fundamentals=False,  # faster without fundamental API calls
    include_nse=False,
)
print(f"Features computed for {len(latest_features)} stocks")

# %%
# Generate ranked picks
TOP_N = 20

picks = predict_and_rank(
    latest_features,
    model,
    meta,
    model_type="lightgbm",
    top_n=TOP_N,
)

print(f"\nTop {TOP_N} Weekly Picks:")
picks

# %% [markdown]
# ### 6.1 — Explain Top Picks

# %%
from screener.live.explain import explain_predictions

explanations = explain_predictions(
    latest_features,
    predictions=picks["PROBABILITY"].values,
    model=model,
    meta=meta,
    model_type="lightgbm",
    top_k=5,
)

for exp in explanations:
    print(f"\n{'='*60}")
    print(f"{exp['symbol']}  —  Probability: {exp['probability']:.1%}")
    print(f"{'='*60}")
    print(exp["explanation"])

# %% [markdown]
# ---
# ## Phase 7 — AlphaForge Integration
#
# Push screener results to the AlphaForge backend API so they appear in the terminal dashboard.

# %%
import httpx
import json
from datetime import date

# AlphaForge backend URL — reads from .env.port or defaults
BACKEND_URL = "http://localhost:8000"


def check_backend_health() -> bool:
    """Check if AlphaForge backend is running."""
    try:
        r = httpx.get(f"{BACKEND_URL}/api/v1/health", timeout=5.0)
        print(f"Backend status: {r.json()}")
        return r.status_code == 200
    except httpx.ConnectError:
        print("Backend not running. Start it with: cd backend && pdm run dev")
        return False


check_backend_health()


# %%
def push_picks_to_backend(picks_df: pd.DataFrame, backend_url: str = BACKEND_URL) -> dict:
    """Push screener picks to AlphaForge backend."""
    payload = {
        "scan_date": str(date.today()),
        "model_type": "lightgbm",
        "picks": [],
    }
    for _, row in picks_df.iterrows():
        pick = {
            "symbol": row["SYMBOL"].replace(".NS", ""),
            "probability": float(row["PROBABILITY"]),
            "rank": int(row["RANK"]),
        }
        # Add key features if present
        for col in ["RSI_14", "MACD_HIST", "ADX_14", "VOL_SMA_RATIO", "DIST_52W_HIGH_PCT"]:
            if col in row.index and pd.notna(row[col]):
                pick[col.lower()] = float(row[col])
        payload["picks"].append(pick)

    try:
        r = httpx.post(
            f"{backend_url}/api/v1/screener/picks",
            json=payload,
            timeout=10.0,
        )
        r.raise_for_status()
        print(f"Pushed {len(payload['picks'])} picks to backend.")
        return r.json()
    except httpx.ConnectError:
        print("Backend not reachable — picks saved locally only.")
        return {"status": "offline", "picks_saved_locally": True}
    except httpx.HTTPStatusError as e:
        print(f"Backend error: {e.response.status_code} — {e.response.text}")
        return {"status": "error", "detail": str(e)}


# Push picks (only if we have them from Phase 6)
if 'picks' in dir() and picks is not None and len(picks) > 0:
    result = push_picks_to_backend(picks)
    print(json.dumps(result, indent=2))
else:
    print("No picks to push — run Phase 6 first.")


# %% [markdown]
# ### 7.1 — Fetch Screener Results from Backend

# %%
def fetch_picks_from_backend(scan_date: str | None = None, backend_url: str = BACKEND_URL) -> pd.DataFrame:
    """Retrieve screener picks from AlphaForge backend."""
    params = {}
    if scan_date:
        params["date"] = scan_date

    try:
        r = httpx.get(
            f"{backend_url}/api/v1/screener/picks",
            params=params,
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("picks"):
            return pd.DataFrame(data["picks"])
        print("No picks returned from backend.")
        return pd.DataFrame()
    except httpx.ConnectError:
        print("Backend not reachable. Reading from local picks instead.")
        # Fallback to local file
        local_picks = list(config.PICKS_DIR.glob("*_weekly_picks.csv"))
        if local_picks:
            latest = sorted(local_picks)[-1]
            print(f"Loading from: {latest.name}")
            return pd.read_csv(latest)
        return pd.DataFrame()


# Fetch latest picks
backend_picks = fetch_picks_from_backend()
if not backend_picks.empty:
    backend_picks

# %% [markdown]
# ---
# ## Quick Run — Full Pipeline in One Cell
#
# Run the entire pipeline end-to-end. Set `QUICK_MODE = True` for a fast test with limited symbols.

# %%
QUICK_MODE = True  # Set False for full universe
QUICK_SYMBOLS = 10  # Number of symbols in quick mode

print("="*60)
print(f"FULL PIPELINE RUN ({'QUICK' if QUICK_MODE else 'FULL'} mode)")
print("="*60)

# Phase 1 — Data (skip if already exists)
from screener.data.fetch_universe import fetch_universe
from screener.data.fetch_ohlcv import fetch_ohlcv
from screener.data.fetch_nse_data import fetch_index_data

if not config.UNIVERSE_FILTERED_FILE.exists():
    print("\n[Phase 1] Fetching universe...")
    fetch_universe()

ohlcv_count = len(list(config.OHLCV_DIR.glob("*.parquet")))
if ohlcv_count < 10:
    print("\n[Phase 1] Downloading OHLCV...")
    fetch_ohlcv(incremental=True)

if not list(config.INDICES_DIR.glob("*.parquet")):
    print("\n[Phase 1] Fetching index data...")
    fetch_index_data()

print(f"[Phase 1] Data ready — {len(list(config.OHLCV_DIR.glob('*.parquet')))} OHLCV files")

# Phase 3 — Dataset
from screener.dataset.build_dataset import build_dataset
print("\n[Phase 3] Building dataset...")
dataset = build_dataset(
    max_symbols=QUICK_SYMBOLS if QUICK_MODE else None,
    include_fundamentals=not QUICK_MODE,
    include_nse=not QUICK_MODE,
    save=True,
)
print(f"[Phase 3] Dataset: {dataset.shape[0]:,} rows × {dataset.shape[1]} cols")

# Phase 4 — Training
from screener.models.train_lightgbm import train_lightgbm
EXCLUDE_COLS = {"SYMBOL", "SECTOR", "MARKET_CAP_CATEGORY",
                "FORWARD_RETURN_5D", "TARGET_5PCT_5D", "Adj Close"}
feature_cols = [c for c in dataset.columns if c not in EXCLUDE_COLS]

print("\n[Phase 4] Training LightGBM...")
lgb_result = train_lightgbm(dataset, feature_cols=feature_cols, save=True)
print(f"[Phase 4] AUC-ROC: {lgb_result['agg_metrics'].get('auc_roc', 'N/A')}")

# Phase 6 — Live Scan
from screener.live.scan import get_available_symbols, compute_features_latest, load_model, predict_and_rank
print("\n[Phase 6] Running live scan...")
model, meta = load_model(model_type="lightgbm")
symbols = get_available_symbols()
latest_features = compute_features_latest(symbols, include_fundamentals=False, include_nse=False)
picks = predict_and_rank(latest_features, model, meta, top_n=20)
print(f"[Phase 6] Generated {len(picks)} picks")

print("\n" + "="*60)
print("PIPELINE COMPLETE")
print("="*60)
picks.head(10)

# %% [markdown]
# ---
#
# > **Disclaimer: This is NOT SEBI registered investment advice. For personal research and educational use only. Past performance does not guarantee future results.**
