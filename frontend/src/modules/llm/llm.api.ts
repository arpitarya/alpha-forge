import api from "@/lib/api";

export const llmApi = {
  complete: (queryType: string, messages: { role: string; content: string }[]) =>
    api.post("/llm/complete", { query_type: queryType, messages }),
  analyzeScreener: (output: string) =>
    api.post("/llm/analyze-screener", { raw_output: output }),
  explainPicks: (output: string) =>
    api.post("/llm/explain-picks", { raw_output: output }),
  getProviders: () => api.get("/llm/providers"),
  getBenchmark: () => api.get("/llm/benchmark"),
  runBenchmark: () => api.post("/llm/benchmark/run"),
};
