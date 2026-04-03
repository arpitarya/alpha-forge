import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Market Data ─────────────────────────────────
export const marketApi = {
  getQuote: (symbol: string) => api.get(`/market/quote/${symbol}`),
  getIndices: () => api.get("/market/indices"),
  search: (q: string) => api.get("/market/search", { params: { q } }),
  getHistory: (symbol: string, interval = "1d", period = "1y") =>
    api.get(`/market/history/${symbol}`, { params: { interval, period } }),
};

// ── Portfolio ───────────────────────────────────
export const portfolioApi = {
  getSummary: () => api.get("/portfolio/summary"),
  getPositions: () => api.get("/portfolio/positions"),
  getOrders: () => api.get("/portfolio/orders"),
};

// ── AI ──────────────────────────────────────────
export const aiApi = {
  chat: (messages: { role: string; content: string }[], context?: Record<string, unknown>) =>
    api.post("/ai/chat", { messages, context }),
  analyze: (symbol: string, analysisType = "comprehensive") =>
    api.post("/ai/analyze", { symbol, analysis_type: analysisType }),
  screener: (strategy = "momentum") => api.get("/ai/screener", { params: { strategy } }),
  sentiment: (symbol: string) => api.get(`/ai/sentiment/${symbol}`),
};

// ── Trade ───────────────────────────────────────
export const tradeApi = {
  placeOrder: (order: Record<string, unknown>) => api.post("/trade/order", order),
  modifyOrder: (orderId: string, updates: Record<string, unknown>) =>
    api.put(`/trade/order/${orderId}`, updates),
  cancelOrder: (orderId: string) => api.delete(`/trade/order/${orderId}`),
};

// ── Auth ────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) => api.post("/auth/login", data),
};

export default api;
