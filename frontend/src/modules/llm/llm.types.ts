export interface LLMResponseData {
  content: string;
  model: string;
  provider: string;
  tokens_used: number;
  latency_ms: number;
  cost: number;
}

export interface LLMProviderStatus {
  provider: string;
  healthy: boolean;
  models: string[];
  default_model: string;
  remaining: Record<string, number>;
  utilization_pct: number;
  is_local: boolean;
}
