import { type UseQueryOptions, useQuery } from "@tanstack/react-query";
import { screenerApi } from "./screener.api";
import type { ScreenerPicksResponse } from "./screener.types";
import { transformScreenerPick } from "./screener.utils";

export function useScreenerPicks(
  date?: string,
  options?: Partial<UseQueryOptions<ScreenerPicksResponse>>,
) {
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

export function useScreenerDates(options?: Partial<UseQueryOptions>) {
  return useQuery({
    queryKey: ["screener", "dates"],
    queryFn: () => screenerApi.getDates().then((r) => r.data as string[]),
    staleTime: 60_000,
    ...options,
  });
}
