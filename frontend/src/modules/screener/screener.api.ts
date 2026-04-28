import api from "@/lib/api";

export const screenerApi = {
  getPicks: (date?: string) =>
    api.get("/screener/picks", { params: date ? { date } : {} }),
  getDates: () => api.get("/screener/dates"),
};
