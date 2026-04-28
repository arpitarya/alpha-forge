import api from "@/lib/api";

export const dashboardApi = {
  getTicker: () => api.get("/dashboard/ticker"),
  getWatchlist: () => api.get("/dashboard/watchlist"),
  getRisk: () => api.get("/dashboard/risk"),
  getBrief: () => api.get("/dashboard/brief"),
  getStats: () => api.get("/dashboard/stats"),
};
