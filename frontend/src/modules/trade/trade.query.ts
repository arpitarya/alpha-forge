import { useMutation } from "@tanstack/react-query";
import { tradeApi } from "./trade.api";

export function usePlaceOrder() {
  return useMutation({
    mutationFn: (order: Record<string, unknown>) =>
      tradeApi.placeOrder(order).then((r) => r.data),
  });
}

export function useModifyOrder() {
  return useMutation({
    mutationFn: (params: { orderId: string; updates: Record<string, unknown> }) =>
      tradeApi.modifyOrder(params.orderId, params.updates).then((r) => r.data),
  });
}

export function useCancelOrder() {
  return useMutation({
    mutationFn: (orderId: string) => tradeApi.cancelOrder(orderId).then((r) => r.data),
  });
}
