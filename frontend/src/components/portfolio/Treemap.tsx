"use client";

import { Card, Text, TreemapCell } from "@alphaforge/solar-orb-ui";
import { useTreemap } from "@/lib/queries";

export function Treemap() {
  const { data, isLoading } = useTreemap();

  if (isLoading || !data) {
    return (
      <Card className="flex h-full items-center justify-center">
        <Text variant="body-sm" tone="subtle">Loading holdings…</Text>
      </Card>
    );
  }

  if (data.cells.length === 0) {
    return (
      <Card className="flex h-full flex-col items-center justify-center gap-2">
        <Text variant="title">No holdings yet</Text>
        <Text variant="body-sm" tone="subtle">
          Upload an export from any broker on the right to see your portfolio here.
        </Text>
      </Card>
    );
  }

  return (
    <Card className="relative h-full overflow-hidden !p-0">
      {data.cells.map((c) => {
        const big = c.width_pct * c.height_pct > 1500;
        return (
          <TreemapCell
            key={`${c.symbol}-${c.left_pct}-${c.top_pct}`}
            symbol={c.symbol}
            sublabel={c.sublabel}
            value={`₹${Math.round(c.value).toLocaleString("en-IN")}`}
            change={`${c.pnl >= 0 ? "+" : ""}${c.pnl_pct.toFixed(2)}%`}
            pnlPct={c.pnl_pct}
            big={big}
            style={{
              left: `${c.left_pct}%`,
              top: `${c.top_pct}%`,
              width: `${c.width_pct}%`,
              height: `${c.height_pct}%`,
            }}
          />
        );
      })}
    </Card>
  );
}
