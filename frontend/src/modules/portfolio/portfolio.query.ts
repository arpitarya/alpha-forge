import { useMutation, useQuery } from "@tanstack/react-query";
import { portfolioApi } from "./portfolio.api";
import type {
  HoldingsResponseDTO,
  RebalanceResponseDTO,
  SourceInfoDTO,
  SyncAllResultDTO,
  TreemapResponseDTO,
} from "./portfolio.types";

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

export function useSyncAll() {
  return useMutation<SyncAllResultDTO>({
    mutationFn: () => portfolioApi.syncAll().then((r) => r.data as SyncAllResultDTO),
  });
}

export function useStartLogin() {
  return useMutation({
    mutationFn: (slug: string) => portfolioApi.startLogin(slug).then((r) => r.data),
  });
}

export function useSubmitOtp() {
  return useMutation({
    mutationFn: (params: { slug: string; code: string }) =>
      portfolioApi.submitOtp(params.slug, params.code).then((r) => r.data),
  });
}

export function useResetSource() {
  return useMutation({
    mutationFn: (slug: string) => portfolioApi.resetSource(slug).then((r) => r.data),
  });
}
