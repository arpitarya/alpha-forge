import api from "@/lib/api";

export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) => api.post("/auth/login", data),
};
