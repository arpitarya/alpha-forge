export interface ScreenerPick {
  symbol: string;
  probability: number;
  rank: number;
  rsi_14?: number;
  macd_hist?: number;
  adx_14?: number;
  vol_sma_ratio?: number;
  dist_52w_high_pct?: number;
}

export interface ScreenerPicksResponse {
  scan_date: string;
  model_type: string | null;
  count: number;
  picks: ScreenerPick[];
}
