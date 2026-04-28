"use client";

import { Card, Icon, ProgressBar, Text } from "@alphaforge/solar-orb-ui";
import { useScreenerPicks } from "@/modules/screener";

export function ScreenerPanel() {
  const { data, isLoading, isError } = useScreenerPicks();

  return (
    <Card glow className="flex h-full flex-col">
      <Card.Header
        title={
          <span className="flex items-center gap-2">
            <Icon name="query_stats" size="sm" className="text-[color:var(--accent)]" />
            Screener
          </span>
        }
        right={
          data?.scan_date ? (
            <Text variant="tag" tone="subtle">{data.scan_date}</Text>
          ) : null
        }
      />

      {isLoading && (
        <div className="flex flex-1 items-center justify-center">
          <Icon name="hourglass_top" size="md" className="text-[color:var(--fg-3)] animate-pulse" />
        </div>
      )}

      {isError && (
        <div className="flex flex-1 flex-col items-center justify-center gap-2">
          <Icon name="cloud_off" size="md" className="text-[color:var(--fg-3)]" />
          <Text variant="caption" tone="subtle">
            Run the screener pipeline to see picks
          </Text>
        </div>
      )}

      {data && data.picks.length === 0 && !isLoading && (
        <div className="flex flex-1 flex-col items-center justify-center gap-2">
          <Icon name="search_off" size="md" className="text-[color:var(--fg-3)]" />
          <Text variant="caption" tone="subtle">
            No picks available — run a scan first
          </Text>
        </div>
      )}

      {data && data.picks.length > 0 && (
        <div className="flex flex-1 flex-col gap-1.5 overflow-y-auto pr-1">
          {data.picks.slice(0, 6).map((pick, i) => {
            const sym = pick.symbol.replace(".NS", "");
            return (
              <div
                key={pick.symbol}
                className="grid grid-cols-[28px_36px_1fr_180px] items-center gap-3 rounded-[var(--radius-sm)] px-2 py-2 transition-colors hover:bg-white/[0.03]"
              >
                <span className="font-mono text-[11px] tabular-nums text-[color:var(--fg-3)]">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="grid h-9 w-9 place-items-center rounded-[var(--radius-sm)] bg-white/5">
                  <Icon name="trending_up" size="sm" className="text-[color:var(--accent)]" />
                </div>
                <div className="min-w-0">
                  <Text className="block truncate text-sm font-bold tracking-tight">
                    {sym}
                  </Text>
                  {pick.rsi_14 != null && (
                    <Text variant="caption" tone="subtle">
                      RSI {pick.rsi_14.toFixed(0)}
                    </Text>
                  )}
                </div>
                <ProgressBar
                  value={pick.probability * 100}
                  showPercentage
                  className="!gap-1"
                />
              </div>
            );
          })}
        </div>
      )}

      <Text variant="caption" tone="subtle" className="text-center pt-2">
        Not SEBI registered investment advice
      </Text>
    </Card>
  );
}
