import { type UseQueryOptions, useMutation, useQuery } from "@tanstack/react-query";
import {
  aiApi,
  dashboardApi,
  llmApi,
  marketApi,
  portfolioApi,
  screenerApi,
  tradeApi,
} from "./api";

// ── Market Data ─────────────────────────────────

export function useQuote(symbol: string, options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["market", "quote", symbol],
    queryFn: () => marketApi.getQuote(symbol).then((r) => r.data),
    enabled: !!symbol,
    staleTime: 2_000,
    ...options,
  });
}

export function useIndices(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["market", "indices"],
    queryFn: () => marketApi.getIndices().then((r) => r.data),
    staleTime: 5_000,
    ...options,
  });
}

export function useMarketSearch(query: string, options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["market", "search", query],
    queryFn: () => marketApi.search(query).then((r) => r.data),
    enabled: query.length >= 2,
    ...options,
  });
}

export function useHistory(
  symbol: string,
  interval = "1d",
  period = "1y",
  options?: Partial<UseQueryOptions>,
) {
  return useQuery({
    queryKey: ["market", "history", symbol, interval, period],
    queryFn: () => marketApi.getHistory(symbol, interval, period).then((r) => r.data),
    enabled: !!symbol,
    ...options,
  });
}

// ── Portfolio ───────────────────────────────────

export function usePortfolioSummary(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: () => portfolioApi.getSummary().then((r) => r.data),
    ...options,
  });
}

export function usePositions(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["portfolio", "positions"],
    queryFn: () => portfolioApi.getPositions().then((r) => r.data),
    ...options,
  });
}

export function useOrders(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["portfolio", "orders"],
    queryFn: () => portfolioApi.getOrders().then((r) => r.data),
    ...options,
  });
}

// ── AI ──────────────────────────────────────────
// NOTE: Everytime a message is typed or change is made into the code update the
// documentation with the same.

export function useAIChat() {
  return useMutation({
    mutationFn: (params: {
      messages: { role: string; content: string }[];
      context?: Record<string, unknown>;
    }) => aiApi.chat(params.messages, params.context).then((r) => r.data),
  });
}

export function useAnalyzeStock() {
  return useMutation({
    mutationFn: (params: { symbol: string; analysisType?: string }) =>
      aiApi.analyze(params.symbol, params.analysisType).then((r) => r.data),
  });
}

export function useScreener(strategy = "momentum", options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["ai", "screener", strategy],
    queryFn: () => aiApi.screener(strategy).then((r) => r.data),
    ...options,
  });
}

export function useSentiment(symbol: string, options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["ai", "sentiment", symbol],
    queryFn: () => aiApi.sentiment(symbol).then((r) => r.data),
    enabled: !!symbol,
    ...options,
  });
}

// ── Trade ───────────────────────────────────────

export function usePlaceOrder() {
  return useMutation({
    mutationFn: (order: Record<string, unknown>) => tradeApi.placeOrder(order).then((r) => r.data),
  });
}

export function useModifyOrder() {
  return useMutation({
    mutationFn: (params: { orderId: string; updates: Record<string, unknown> }) =>
      tradeApi.modifyOrder(params.orderId, params.updates).then((r) => r.data),
  });
}

export function useCancelOrder() {
  return useMutation({
    mutationFn: (orderId: string) => tradeApi.cancelOrder(orderId).then((r) => r.data),
  });
}

// ── Screener ────────────────────────────────────

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

/**
 * Transform raw API response (uppercase snake_case strings) to typed ScreenerPick
 * @param raw - API response with uppercase keys and string values
 * @returns Typed ScreenerPick object
 */
export function transformScreenerPick(raw: Record<string, unknown>): ScreenerPick {
  return {
    symbol: String(raw.SYMBOL),
    probability: parseFloat(String(raw.PROBABILITY)),
    rank: parseInt(String(raw.RANK), 10),
    rsi_14: raw.RSI_14 ? parseFloat(String(raw.RSI_14)) : undefined,
    macd_hist: raw.MACD_HIST ? parseFloat(String(raw.MACD_HIST)) : undefined,
    adx_14: raw.ADX_14 ? parseFloat(String(raw.ADX_14)) : undefined,
    vol_sma_ratio: raw.VOL_SMA_RATIO ? parseFloat(String(raw.VOL_SMA_RATIO)) : undefined,
    dist_52w_high_pct: raw.DIST_52W_HIGH_PCT ? parseFloat(String(raw.DIST_52W_HIGH_PCT)) : undefined,
  };
}

export interface ScreenerPicksResponse {
  scan_date: string;
  model_type: string | null;
  count: number;
  picks: ScreenerPick[];
}

export function useScreenerPicks(date?: string, options?: Partial<UseQueryOptions<ScreenerPicksResponse>>) {
  return useQuery<ScreenerPicksResponse>({
    queryKey: ["screener", "picks", date ?? "latest"],
    queryFn: () =>
      screenerApi.getPicks(date).then((r) => {
        const data = r.data as ScreenerPicksResponse;
        return {
          ...data,
          picks: data.picks.map((pick) =>
            transformScreenerPick(pick as unknown as Record<string, unknown>),
          ),
        };
      }),
    staleTime: 60_000,
    ...options,
  });
}

// ── Portfolio holdings + sources ───────────────────

export type AssetClass =
  | "equity"
  | "mutual_fund"
  | "etf"
  | "bond"
  | "gold"
  | "crypto"
  | "cash"
  | "other";

export interface HoldingDTO {
  source: string;
  asset_class: AssetClass;
  symbol: string;
  name: string | null;
  isin: string | null;
  quantity: number;
  avg_price: number;
  last_price: number;
  invested: number;
  current_value: number;
  pnl: number;
  pnl_pct: number;
  exchange: string | null;
  sector: string | null;
  as_of: string;
}

export interface AllocationSliceDTO {
  asset_class: AssetClass;
  value: number;
  pct: number;
}

export interface HoldingsResponseDTO {
  totals: {
    invested: number;
    current_value: number;
    pnl: number;
    pnl_pct: number;
    count: number;
  };
  allocation: AllocationSliceDTO[];
  holdings: HoldingDTO[];
  disclaimer: string;
}

export interface TreemapCellDTO {
  symbol: string;
  sublabel: string;
  value: number;
  pct: number;
  pnl: number;
  pnl_pct: number;
  asset_class: AssetClass;
  left_pct: number;
  top_pct: number;
  width_pct: number;
  height_pct: number;
}

export interface TreemapResponseDTO {
  totals: HoldingsResponseDTO["totals"];
  cells: TreemapCellDTO[];
  disclaimer: string;
}

export interface RebalanceResponseDTO {
  drift: Array<{
    asset_class: AssetClass;
    target_pct: number;
    actual_pct: number;
    drift_pct: number;
  }>;
  suggestions: Array<{ action: string }>;
  targets: Record<string, number>;
  disclaimer: string;
}

export type SourceKind = "api" | "csv";
export type SourceStatus = "unconfigured" | "ready" | "syncing" | "error";

export interface SourceInfoDTO {
  slug: string;
  label: string;
  kind: SourceKind;
  status: SourceStatus;
  holdings_count: number;
  last_synced_at: string | null;
  error_message: string | null;
  notes: string | null;
}

export function useHoldings(source?: string) {
  return useQuery<HoldingsResponseDTO>({
    queryKey: ["portfolio", "holdings", source ?? "all"],
    queryFn: () => portfolioApi.getHoldings(source).then((r) => r.data),
    staleTime: 10_000,
  });
}

export function useTreemap(source?: string) {
  return useQuery<TreemapResponseDTO>({
    queryKey: ["portfolio", "treemap", source ?? "all"],
    queryFn: () => portfolioApi.getTreemap(source).then((r) => r.data),
    staleTime: 10_000,
  });
}

export function useRebalance() {
  return useQuery<RebalanceResponseDTO>({
    queryKey: ["portfolio", "rebalance"],
    queryFn: () => portfolioApi.getRebalance().then((r) => r.data),
    staleTime: 30_000,
  });
}

export function useSources() {
  return useQuery<{ sources: SourceInfoDTO[] }>({
    queryKey: ["portfolio", "sources"],
    queryFn: () => portfolioApi.listSources().then((r) => r.data),
    staleTime: 5_000,
  });
}

export function useUploadCsv() {
  return useMutation({
    mutationFn: (params: { slug: string; file: File }) =>
      portfolioApi.uploadCsv(params.slug, params.file).then((r) => r.data),
  });
}

export function useSyncSource() {
  return useMutation({
    mutationFn: (slug: string) => portfolioApi.syncSource(slug).then((r) => r.data),
  });
}

export function useResetSource() {
  return useMutation({
    mutationFn: (slug: string) => portfolioApi.resetSource(slug).then((r) => r.data),
  });
}

// ── Dashboard (terminal home) ──────────────────────

export interface TickerItemDTO {
  symbol: string;
  price: string;
  change: string;
  tone: "up" | "dn";
}
export interface WatchlistItemDTO {
  symbol: string;
  sublabel: string;
  price: string;
  change: string;
  tone: "up" | "dn";
}
export interface RiskMeterDTO {
  bars: number[];
  active_index: number;
  confidence: number;
}
export interface BriefBlockDTO {
  title: string;
  body: string;
  cta: string;
  accent?: boolean;
}
export interface TerminalBriefDTO {
  blocks: BriefBlockDTO[];
  generated_at: string;
  disclaimer: string;
}
export interface StatCardDTO {
  label: string;
  value: number;
  delta: string;
  delta_tone: "up" | "dn" | "neutral" | "accent";
  sparkline: number[] | null;
}
export interface DashboardStatsDTO {
  net_worth: StatCardDTO;
  pnl_today: StatCardDTO;
  confidence: StatCardDTO;
  disclaimer: string;
}

export function useDashboardTicker() {
  return useQuery<TickerItemDTO[]>({
    queryKey: ["dashboard", "ticker"],
    queryFn: () => dashboardApi.getTicker().then((r) => r.data),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}
export function useDashboardWatchlist() {
  return useQuery<WatchlistItemDTO[]>({
    queryKey: ["dashboard", "watchlist"],
    queryFn: () => dashboardApi.getWatchlist().then((r) => r.data),
    staleTime: 5_000,
    refetchInterval: 5_000,
  });
}
export function useDashboardRisk() {
  return useQuery<RiskMeterDTO>({
    queryKey: ["dashboard", "risk"],
    queryFn: () => dashboardApi.getRisk().then((r) => r.data),
    staleTime: 4_000,
    refetchInterval: 4_000,
  });
}
export function useDashboardBrief() {
  return useQuery<TerminalBriefDTO>({
    queryKey: ["dashboard", "brief"],
    queryFn: () => dashboardApi.getBrief().then((r) => r.data),
    staleTime: 60_000,
  });
}
export function useDashboardStats() {
  return useQuery<DashboardStatsDTO>({
    queryKey: ["dashboard", "stats"],
    queryFn: () => dashboardApi.getStats().then((r) => r.data),
    staleTime: 5_000,
    refetchInterval: 5_000,
  });
}

export function useScreenerDates(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["screener", "dates"],
    queryFn: () => screenerApi.getDates().then((r) => r.data as string[]),
    staleTime: 60_000,
    ...options,
  });
}

// ── LLM Gateway ─────────────────────────────

export interface LLMResponseData {
  content: string;
  model: string;
  provider: string;
  tokens_used: number;
  latency_ms: number;
  cost: number;
}

export interface LLMProviderStatus {
  provider: string;
  healthy: boolean;
  models: string[];
  default_model: string;
  remaining: Record<string, number>;
  utilization_pct: number;
  is_local: boolean;
}

export function useAnalyzeScreener() {
  return useMutation({
    mutationFn: (output: string) =>
      llmApi.analyzeScreener(output).then((r) => r.data as LLMResponseData),
  });
}

export function useExplainPicks() {
  return useMutation({
    mutationFn: (output: string) =>
      llmApi.explainPicks(output).then((r) => r.data as LLMResponseData),
  });
}

export function useLLMProviders(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["llm", "providers"],
    queryFn: () => llmApi.getProviders().then((r) => r.data as LLMProviderStatus[]),
    staleTime: 30_000,
    ...options,
  });
}

export function useBenchmarkResults(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["llm", "benchmark"],
    queryFn: () => llmApi.getBenchmark().then((r) => r.data),
    staleTime: 300_000,
    ...options,
  });
}
