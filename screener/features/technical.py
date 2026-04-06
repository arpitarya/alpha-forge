"""Phase 2.1 — Technical Indicators.

Computes ~30 technical indicators per stock using the `ta` library.
Groups: Momentum, Trend, Volatility, Volume, Price Action.

All features are computed using only data available up to that day (no lookahead).

Disclaimer: NOT SEBI registered investment advice. For personal research only.
"""

import logging

import numpy as np
import pandas as pd
from ta.momentum import (
    RSIIndicator,
    StochasticOscillator,
    WilliamsRIndicator,
    ROCIndicator,
)
from ta.trend import (
    MACD,
    ADXIndicator,
    AroonIndicator,
    SMAIndicator,
)
from ta.volatility import (
    BollingerBands,
    AverageTrueRange,
    KeltnerChannel,
)
from ta.volume import (
    OnBalanceVolumeIndicator,
    AccDistIndexIndicator,
    MFIIndicator,
)

logger = logging.getLogger(__name__)


def compute_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """Momentum indicators: RSI, Stochastic, Williams %R, ROC."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    features = pd.DataFrame(index=df.index)

    # RSI
    features["RSI_14"] = RSIIndicator(close=close, window=14).rsi()
    features["RSI_7"] = RSIIndicator(close=close, window=7).rsi()

    # Stochastic Oscillator
    stoch = StochasticOscillator(high=high, low=low, close=close, window=14, smooth_window=3)
    features["STOCH_K"] = stoch.stoch()
    features["STOCH_D"] = stoch.stoch_signal()

    # Williams %R
    features["WILLIAMS_R"] = WilliamsRIndicator(high=high, low=low, close=close, lbp=14).williams_r()

    # Rate of Change
    features["ROC_5"] = ROCIndicator(close=close, window=5).roc()
    features["ROC_10"] = ROCIndicator(close=close, window=10).roc()
    features["ROC_20"] = ROCIndicator(close=close, window=20).roc()

    return features


def compute_trend_features(df: pd.DataFrame) -> pd.DataFrame:
    """Trend indicators: MACD, ADX, Aroon, SMA crossovers."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    features = pd.DataFrame(index=df.index)

    # MACD
    macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
    features["MACD_LINE"] = macd.macd()
    features["MACD_SIGNAL"] = macd.macd_signal()
    features["MACD_HIST"] = macd.macd_diff()

    # ADX
    adx = ADXIndicator(high=high, low=low, close=close, window=14)
    features["ADX_14"] = adx.adx()
    features["ADX_POS"] = adx.adx_pos()
    features["ADX_NEG"] = adx.adx_neg()

    # Aroon
    aroon = AroonIndicator(high=high, low=low, window=25)
    features["AROON_UP"] = aroon.aroon_up()
    features["AROON_DOWN"] = aroon.aroon_down()

    # SMA cross signals (binary: 1 if short > long, 0 otherwise)
    sma_20 = SMAIndicator(close=close, window=20).sma_indicator()
    sma_50 = SMAIndicator(close=close, window=50).sma_indicator()
    sma_200 = SMAIndicator(close=close, window=200).sma_indicator()

    features["SMA_20_50_CROSS"] = (sma_20 > sma_50).astype(int)
    features["SMA_50_200_CROSS"] = (sma_50 > sma_200).astype(int)
    features["PRICE_ABOVE_SMA_20"] = (close > sma_20).astype(int)
    features["PRICE_ABOVE_SMA_50"] = (close > sma_50).astype(int)
    features["PRICE_ABOVE_SMA_200"] = (close > sma_200).astype(int)

    return features


def compute_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """Volatility indicators: Bollinger Bands, ATR, Keltner Channel."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    features = pd.DataFrame(index=df.index)

    # Bollinger Bands
    bb = BollingerBands(close=close, window=20, window_dev=2)
    bb_high = bb.bollinger_hband()
    bb_low = bb.bollinger_lband()
    bb_width = bb_high - bb_low
    bb_mid = bb.bollinger_mavg()

    # %B: (Close - Lower) / (Upper - Lower)
    features["BB_PCT_B"] = bb.bollinger_pband()
    # Bandwidth: (Upper - Lower) / Middle
    features["BB_BANDWIDTH"] = bb_width / bb_mid.replace(0, np.nan)

    # ATR
    features["ATR_14"] = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()
    # ATR as percentage of close for cross-stock comparability
    features["ATR_14_PCT"] = features["ATR_14"] / close.replace(0, np.nan)

    # Keltner Channel position: (Close - KC_mid) / (KC_high - KC_low)
    kc = KeltnerChannel(high=high, low=low, close=close, window=20)
    kc_high = kc.keltner_channel_hband()
    kc_low = kc.keltner_channel_lband()
    kc_range = kc_high - kc_low
    kc_mid = kc.keltner_channel_mband()
    features["KC_POSITION"] = (close - kc_mid) / kc_range.replace(0, np.nan)

    return features


def compute_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """Volume indicators: OBV, Volume ratio, A/D, MFI."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"].astype(float)

    features = pd.DataFrame(index=df.index)

    # On-Balance Volume (normalized as pct change)
    obv = OnBalanceVolumeIndicator(close=close, volume=volume).on_balance_volume()
    features["OBV"] = obv
    features["OBV_ROC_5"] = obv.pct_change(periods=5)

    # Volume SMA ratio: today's volume / 20-day avg volume
    vol_sma_20 = volume.rolling(window=20).mean()
    features["VOL_SMA_RATIO"] = volume / vol_sma_20.replace(0, np.nan)

    # Accumulation/Distribution
    features["AD_LINE"] = AccDistIndexIndicator(
        high=high, low=low, close=close, volume=volume
    ).acc_dist_index()

    # Money Flow Index (volume-weighted RSI)
    features["MFI_14"] = MFIIndicator(
        high=high, low=low, close=close, volume=volume, window=14
    ).money_flow_index()

    return features


def compute_price_action_features(df: pd.DataFrame) -> pd.DataFrame:
    """Price action features: 52w high/low distance, consecutive days, gaps, candle body."""
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    open_ = df["Open"]

    features = pd.DataFrame(index=df.index)

    # Distance from 52-week (252 trading days) high/low as percentage
    high_252 = high.rolling(window=252, min_periods=50).max()
    low_252 = low.rolling(window=252, min_periods=50).min()
    features["DIST_52W_HIGH_PCT"] = (close - high_252) / high_252.replace(0, np.nan)
    features["DIST_52W_LOW_PCT"] = (close - low_252) / low_252.replace(0, np.nan)

    # Consecutive up/down days
    daily_return = close.pct_change()
    up = (daily_return > 0).astype(int)
    down = (daily_return < 0).astype(int)

    # Count consecutive up days
    reset_up = up.eq(0)
    groups_up = reset_up.cumsum()
    features["CONSEC_UP_DAYS"] = up.groupby(groups_up).cumsum()

    # Count consecutive down days
    reset_down = down.eq(0)
    groups_down = reset_down.cumsum()
    features["CONSEC_DOWN_DAYS"] = down.groupby(groups_down).cumsum()

    # Gap up/down percentage: (today's open - yesterday's close) / yesterday's close
    features["GAP_PCT"] = (open_ - close.shift(1)) / close.shift(1).replace(0, np.nan)

    # Candle body ratio: |Close - Open| / (High - Low)
    body = (close - open_).abs()
    wick = high - low
    features["CANDLE_BODY_RATIO"] = body / wick.replace(0, np.nan)

    return features


def compute_technical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all technical indicators for a single stock's OHLCV DataFrame.

    Args:
        df: DataFrame with columns [Open, High, Low, Close, Volume] and DatetimeIndex.

    Returns:
        DataFrame with ~30+ technical features, same index as input.
    """
    required_cols = {"Open", "High", "Low", "Close", "Volume"}
    # Handle MultiIndex columns (flatten if needed)
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    momentum = compute_momentum_features(df)
    trend = compute_trend_features(df)
    volatility = compute_volatility_features(df)
    volume = compute_volume_features(df)
    price_action = compute_price_action_features(df)

    features = pd.concat([momentum, trend, volatility, volume, price_action], axis=1)

    logger.debug("Computed %d technical features, %d rows", features.shape[1], features.shape[0])
    return features


if __name__ == "__main__":
    import sys
    from pathlib import Path

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from config import OHLCV_DIR

    # Test with RELIANCE
    symbol = "RELIANCE"
    filepath = OHLCV_DIR / f"{symbol}.parquet"
    if not filepath.exists():
        print(f"No data for {symbol}. Run fetch_ohlcv.py first.")
        sys.exit(1)

    df = pd.read_parquet(filepath)
    features = compute_technical_features(df)
    print(f"\n{symbol} technical features:")
    print(f"  Shape: {features.shape}")
    print(f"  Columns ({features.shape[1]}):")
    for col in features.columns:
        non_null = features[col].notna().sum()
        print(f"    {col:30s} — {non_null}/{len(features)} non-null")
    print(f"\nLast row sample:")
    print(features.iloc[-1].to_string())
