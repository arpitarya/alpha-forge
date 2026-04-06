"use client";

import { useScreenerPicks } from "@/lib/queries";
import type { ScreenerPick } from "@/lib/queries";

function ProbabilityBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 rounded-full bg-white/10 overflow-hidden">
        <div
          className="h-full rounded-full bg-primary/80 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[10px] text-white/50 tabular-nums">{pct}%</span>
    </div>
  );
}

function PickRow({ pick, index }: { pick: ScreenerPick; index: number }) {
  const symbol = pick.SYMBOL.replace(".NS", "");
  return (
    <div className="flex items-center justify-between group cursor-pointer hover:bg-white/[0.02] rounded-xl px-2 py-2 -mx-2 transition-colors">
      <div className="flex gap-3 items-center">
        <span className="text-[10px] text-white/20 w-4 tabular-nums">{index + 1}</span>
        <div className="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
          <span className="material-symbols-outlined text-primary text-sm">trending_up</span>
        </div>
        <div>
          <p className="font-bold text-xs tracking-tight">{symbol}</p>
          {pick.rsi_14 != null && (
            <p className="text-[9px] text-white/30 tabular-nums">
              RSI {pick.rsi_14.toFixed(0)}
            </p>
          )}
        </div>
      </div>
      <ProbabilityBar value={pick.probability} />
    </div>
  );
}

export function ScreenerPicks() {
  const { data, isLoading, isError } = useScreenerPicks();

  return (
    <section className="h-full floating-shard rounded-[2.5rem] p-10 flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-primary text-xl">
            query_stats
          </span>
          <h2 className="text-sm font-bold tracking-[0.3em] uppercase text-white/90">
            Screener
          </h2>
        </div>
        {data?.scan_date && (
          <span className="text-[9px] text-white/25 tabular-nums tracking-wider uppercase">
            {data.scan_date}
          </span>
        )}
      </div>

      {isLoading && (
        <div className="flex-1 flex items-center justify-center">
          <span className="material-symbols-outlined text-white/10 text-3xl animate-pulse">
            hourglass_top
          </span>
        </div>
      )}

      {isError && (
        <div className="flex-1 flex flex-col items-center justify-center gap-2">
          <span className="material-symbols-outlined text-white/10 text-2xl">
            cloud_off
          </span>
          <p className="text-[10px] text-white/25">
            Run the screener pipeline to see picks
          </p>
        </div>
      )}

      {data && data.picks.length === 0 && !isLoading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-2">
          <span className="material-symbols-outlined text-white/10 text-2xl">
            search_off
          </span>
          <p className="text-[10px] text-white/25">
            No picks available — run a scan first
          </p>
        </div>
      )}

      {data && data.picks.length > 0 && (
        <>
          <div className="space-y-1 overflow-y-auto flex-1 -mr-4 pr-4">
            {data.picks.slice(0, 10).map((pick, i) => (
              <PickRow key={pick.symbol} pick={pick} index={i} />
            ))}
          </div>
          <p className="text-[8px] text-white/15 text-center tracking-wider">
            Not SEBI registered investment advice
          </p>
        </>
      )}
    </section>
  );
}
