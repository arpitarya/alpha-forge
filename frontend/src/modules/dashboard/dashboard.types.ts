export interface TickerItemDTO {
  symbol: string;
  price: string;
  change: string;
  tone: "up" | "dn";
}

export interface WatchlistItemDTO {
  symbol: string;
  sublabel: string;
  price: string;
  change: string;
  tone: "up" | "dn";
}

export interface RiskMeterDTO {
  bars: number[];
  active_index: number;
  confidence: number;
}

export interface BriefBlockDTO {
  title: string;
  body: string;
  cta: string;
  accent?: boolean;
}

export interface TerminalBriefDTO {
  blocks: BriefBlockDTO[];
  generated_at: string;
  disclaimer: string;
}

export interface StatCardDTO {
  label: string;
  value: number;
  delta: string;
  delta_tone: "up" | "dn" | "neutral" | "accent";
  sparkline: number[] | null;
}

export interface DashboardStatsDTO {
  net_worth: StatCardDTO;
  pnl_today: StatCardDTO;
  confidence: StatCardDTO;
  disclaimer: string;
}
