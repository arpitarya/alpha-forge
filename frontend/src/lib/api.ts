import axios from "axios";
import { getLogger } from "@/lib/logger";

const log = getLogger("api");

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("af_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    log.error(
      { status: error.response?.status, url: error.config?.url },
      "API request failed: %s",
      error.message,
    );
    return Promise.reject(error);
  },
);

export default api;
