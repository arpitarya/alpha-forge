"use client";

import {
  Button,
  Card,
  Chip,
  ProgressBar,
  Text,
} from "@alphaforge/solar-orb-ui";
import { useRebalance } from "@/lib/queries";

const CLASS_LABEL: Record<string, string> = {
  equity: "Equity",
  mutual_fund: "MF",
  etf: "ETF",
  bond: "Bond",
  gold: "Gold",
  crypto: "Crypto",
  cash: "Cash",
  other: "Other",
};

export function RebalanceRail() {
  const { data } = useRebalance();
  const drift = data?.drift ?? [];
  const suggestions = data?.suggestions ?? [];

  return (
    <Card glow className="flex h-full flex-col gap-4 overflow-auto">
      <div className="flex items-center gap-3">
        <div
          className="h-8 w-8 rounded-full"
          style={{
            background:
              "radial-gradient(circle at 36% 34%, #fff, var(--accent-soft) 25%, var(--accent) 65%, transparent)",
            boxShadow: "0 0 20px var(--glow)",
          }}
          aria-hidden
        />
        <div className="flex flex-col">
          <Text variant="tag" tone="accent">Alpha · Rebalance</Text>
          <Text variant="title">Drift vs target allocation</Text>
        </div>
      </div>

      <div className="flex flex-col gap-3 border-l-2 border-[color:var(--accent)] pl-3">
        <Text variant="body" tone="muted">
          Targets are a balanced default (60/15/15/5/3/2). Suggestions below
          fire when any class drifts more than ±5%.
        </Text>
      </div>

      {suggestions.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {suggestions.map((s, i) => (
            <Chip key={`${s.action}-${i}`} variant="bordered">
              {s.action}
            </Chip>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-2.5">
        {drift.map((d) => (
          <ProgressBar
            key={d.asset_class}
            bidirectional
            value={d.drift_pct * 4} // amplify for visibility
            label={CLASS_LABEL[d.asset_class] ?? d.asset_class}
            showPercentage
          />
        ))}
      </div>

      <Button variant="deploy" size="lg" className="mt-auto w-full">
        Simulate &amp; backtest
      </Button>

      {data?.disclaimer && (
        <Text variant="caption" tone="subtle" className="text-center">
          {data.disclaimer}
        </Text>
      )}
    </Card>
  );
}
