import { type UseQueryOptions, useMutation, useQuery } from "@tanstack/react-query";
import { aiApi, llmApi, marketApi, portfolioApi, screenerApi, tradeApi } from "./api";

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
  SYMBOL: string;
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

export function useScreenerPicks(date?: string, options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["screener", "picks", date ?? "latest"],
    queryFn: () => screenerApi.getPicks(date).then((r) => r.data as ScreenerPicksResponse),
    staleTime: 60_000,
    ...options,
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
