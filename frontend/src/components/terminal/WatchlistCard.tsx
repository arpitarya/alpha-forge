"use client";

import { Card, RiskBars, Text, WatchRow } from "@alphaforge/solar-orb-ui";
import { useDashboardRisk, useDashboardWatchlist } from "@/lib/queries";

export function WatchlistCard() {
  const { data: items = [] } = useDashboardWatchlist();
  const { data: risk } = useDashboardRisk();

  return (
    <Card glow className="flex h-full flex-col overflow-auto">
      <Card.Header
        title="Watchlist"
        right={<Text variant="tag" tone="subtle">+ ADD</Text>}
      />
      <div className="flex flex-col">
        {items.map((it) => (
          <WatchRow
            key={it.symbol}
            symbol={it.symbol}
            sublabel={it.sublabel}
            price={it.price}
            change={it.change}
            changeTone={it.tone}
            className="border-b border-dashed border-[color:var(--line-hi)] last:border-b-0"
          />
        ))}
      </div>

      <hr className="my-3 h-px border-0 bg-[color:var(--line-hi)]" />

      <Card.Header
        title="Risk Meter"
        right={
          <Text variant="tag" tone="accent">
            {risk ? `${risk.confidence.toFixed(1)}%` : "—"}
          </Text>
        }
      />
      {risk && <RiskBars values={risk.bars} activeIndex={risk.active_index} height={64} />}
      {risk && (
        <div className="mt-3 flex justify-between font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)]">
          <span>Confidence</span>
          <span className="text-[color:var(--accent)]">{risk.confidence.toFixed(1)} / 100</span>
        </div>
      )}
    </Card>
  );
}
