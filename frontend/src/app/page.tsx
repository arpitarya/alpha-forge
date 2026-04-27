import { AppShell } from "@alphaforge/solar-orb-ui";
import {
  AlphaBriefCard,
  OrbStage,
  ScreenerPanel,
  TerminalRail,
  TerminalStats,
  TerminalTicker,
  TerminalTopBar,
  TerminalVoice,
  WatchlistCard,
} from "@/components/terminal";

export default function Home() {
  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
      rail={<TerminalRail />}
      footer={<TerminalVoice />}
    >
      <div className="grid h-full grid-cols-12 grid-rows-[1fr_auto] gap-3 min-h-0">
        {/* Left: Alpha Brief */}
        <div className="col-span-3 row-span-2 min-h-0">
          <AlphaBriefCard />
        </div>

        {/* Center: Orb + stats */}
        <section className="col-span-6 flex min-h-0 flex-col gap-3">
          <div className="flex-1 min-h-0">
            <OrbStage />
          </div>
          <TerminalStats />
        </section>

        {/* Right: Watchlist + Risk Meter */}
        <div className="col-span-3 row-span-2 min-h-0">
          <WatchlistCard />
        </div>
      </div>
    </AppShell>
  );
}
