import type { ScreenerPick } from "./screener.types";

export function transformScreenerPick(raw: Record<string, unknown>): ScreenerPick {
  return {
    symbol: String(raw.SYMBOL),
    probability: parseFloat(String(raw.PROBABILITY)),
    rank: parseInt(String(raw.RANK), 10),
    rsi_14: raw.RSI_14 ? parseFloat(String(raw.RSI_14)) : undefined,
    macd_hist: raw.MACD_HIST ? parseFloat(String(raw.MACD_HIST)) : undefined,
    adx_14: raw.ADX_14 ? parseFloat(String(raw.ADX_14)) : undefined,
    vol_sma_ratio: raw.VOL_SMA_RATIO ? parseFloat(String(raw.VOL_SMA_RATIO)) : undefined,
    dist_52w_high_pct: raw.DIST_52W_HIGH_PCT
      ? parseFloat(String(raw.DIST_52W_HIGH_PCT))
      : undefined,
  };
}
