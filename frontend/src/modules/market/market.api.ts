import api from "@/lib/api";

export const marketApi = {
  getQuote: (symbol: string) => api.get(`/market/quote/${symbol}`),
  getIndices: () => api.get("/market/indices"),
  search: (q: string) => api.get("/market/search", { params: { q } }),
  getHistory: (symbol: string, interval = "1d", period = "1y") =>
    api.get(`/market/history/${symbol}`, { params: { interval, period } }),
};
