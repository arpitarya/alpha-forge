import { type UseQueryOptions, useQuery } from "@tanstack/react-query";
import { marketApi } from "./market.api";

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
