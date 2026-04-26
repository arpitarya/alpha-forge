"use client";

import { CountUp, Sparkline, Stat } from "@alphaforge/solar-orb-ui";
import { useDashboardStats } from "@/lib/queries";

export function TerminalStats() {
  const { data } = useDashboardStats();

  if (!data) {
    return (
      <div className="grid grid-cols-3 gap-3">
        <Stat label="Net Worth" value="—" />
        <Stat label="Today's P&L" value="—" />
        <Stat label="Confidence" value="—" />
      </div>
    );
  }

  const { net_worth, pnl_today, confidence } = data;

  return (
    <div className="grid grid-cols-3 gap-3">
      <Stat
        label={net_worth.label}
        value={<CountUp value={net_worth.value} format="inr" prefix="₹" />}
        delta={net_worth.delta}
        deltaTone={net_worth.delta_tone}
        sparkline={
          net_worth.sparkline
            ? { points: net_worth.sparkline, tone: "accent", fill: true }
            : undefined
        }
      />
      <Stat
        label={pnl_today.label}
        value={<CountUp value={pnl_today.value} prefix="+₹" />}
        delta={pnl_today.delta}
        deltaTone={pnl_today.delta_tone}
      />
      <Stat
        label={confidence.label}
        value={<CountUp value={confidence.value} decimals={1} suffix="%" />}
        delta={confidence.delta}
        deltaTone={confidence.delta_tone}
      />
    </div>
  );
}

// Re-export Sparkline so the page tree-shakes cleanly if needed elsewhere.
export { Sparkline };
