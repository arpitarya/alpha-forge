import { type UseQueryOptions, useMutation, useQuery } from "@tanstack/react-query";
import { llmApi } from "./llm.api";
import type { LLMProviderStatus, LLMResponseData } from "./llm.types";

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
