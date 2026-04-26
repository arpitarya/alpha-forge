"use client";

import { AppShell } from "@alphaforge/solar-orb-ui";
import { useState } from "react";
import {
  Ledger,
  PortfolioHeader,
  type PortfolioView,
  RebalanceRail,
  SourcesPanel,
  Treemap,
} from "@/components/portfolio";
import {
  TerminalRail,
  TerminalTicker,
  TerminalTopBar,
  TerminalVoice,
} from "@/components/terminal";

export default function PortfolioPage() {
  const [view, setView] = useState<PortfolioView>("tree");

  return (
    <AppShell
      header={<TerminalTopBar />}
      ticker={<TerminalTicker />}
      rail={<TerminalRail />}
      footer={<TerminalVoice />}
    >
      <div className="grid h-full grid-cols-12 grid-rows-[auto_1fr_auto] gap-3 min-h-0">
        {/* Header strip */}
        <div className="col-span-12">
          <PortfolioHeader view={view} onViewChange={setView} />
        </div>

        {/* Main: treemap or ledger */}
        <div className="col-span-9 min-h-0">
          {view === "tree" ? <Treemap /> : <Ledger />}
        </div>

        {/* Right rail: rebalance */}
        <div className="col-span-3 row-span-2 min-h-0">
          <RebalanceRail />
        </div>

        {/* Bottom: sources management */}
        <div className="col-span-9 min-h-0 max-h-[280px]">
          <SourcesPanel />
        </div>
      </div>
    </AppShell>
  );
}
