"""AlphaForge Screener — Configuration.

Paths, thresholds, index symbols, and constants used across the data pipeline.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OHLCV_DIR = RAW_DIR / "ohlcv"
INDICES_DIR = RAW_DIR / "indices"
NSE_SUPP_DIR = RAW_DIR / "nse_supplementary"
FEATURES_DIR = BASE_DIR / "features"
DATASET_DIR = BASE_DIR / "dataset"
MODELS_DIR = BASE_DIR / "models" / "saved"
REPORTS_DIR = BASE_DIR / "reports"
PICKS_DIR = BASE_DIR / "live" / "picks"

# Ensure critical dirs exist at import time
for _d in (RAW_DIR, OHLCV_DIR, INDICES_DIR, NSE_SUPP_DIR, MODELS_DIR, REPORTS_DIR, PICKS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ── Universe Filters ───────────────────────────────────────────────────────────
VALID_SERIES = {"EQ"}  # Keep only regular equity series
MIN_AVG_VOLUME_90D = 10_000  # Minimum 90-day average daily volume
OHLCV_HISTORY_YEARS = 2  # Years of daily OHLCV to download

# ── yfinance Settings ─────────────────────────────────────────────────────────
YFINANCE_BATCH_SIZE = 500  # Max tickers per yfinance.download() call
YFINANCE_SUFFIX = ".NS"  # NSE suffix for yfinance symbols

# ── NSE Data Settings ─────────────────────────────────────────────────────────
NSE_REQUEST_DELAY = 0.5  # Seconds between nselib API calls (avoid rate-limiting)

# ── Index Benchmarks ──────────────────────────────────────────────────────────
INDEX_SYMBOLS: dict[str, str] = {
    "NIFTY_50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK_NIFTY": "^NSEBANK",
    "NIFTY_IT": "^CNXIT",
}

# ── Target / Label ────────────────────────────────────────────────────────────
TARGET_RETURN_THRESHOLD = 0.05  # 5% return threshold for positive label
TARGET_FORWARD_DAYS = 5  # Trading days to look ahead

# ── Output Files ──────────────────────────────────────────────────────────────
UNIVERSE_FILE = RAW_DIR / "universe.csv"
UNIVERSE_FILTERED_FILE = RAW_DIR / "universe_filtered.csv"
