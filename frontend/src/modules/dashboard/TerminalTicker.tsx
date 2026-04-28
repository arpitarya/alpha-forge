"use client";

import { Ticker } from "@alphaforge/solar-orb-ui";
import { useDashboardTicker } from "@/modules/dashboard";

export function TerminalTicker() {
  const { data: items = [] } = useDashboardTicker();

  if (items.length === 0) {
    return (
      <div className="h-7 rounded-[var(--radius-sm)] border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)]" />
    );
  }

  return <Ticker items={items} speedSeconds={48} />;
}
