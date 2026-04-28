import api from "@/lib/api";

export const tradeApi = {
  placeOrder: (order: Record<string, unknown>) => api.post("/trade/order", order),
  modifyOrder: (orderId: string, updates: Record<string, unknown>) =>
    api.put(`/trade/order/${orderId}`, updates),
  cancelOrder: (orderId: string) => api.delete(`/trade/order/${orderId}`),
};
