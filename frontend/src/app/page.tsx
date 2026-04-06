import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import {
  Allocation,
  AlphaBrief,
  NetWorth,
  RiskAnalysis,
  ScreenerPicks,
  SolarOrb,
  TerminalWatchlist,
  VoiceFooter,
} from "@/components/terminal";

export default function Home() {
  return (
    <div className="flex h-screen flex-col bg-black overflow-hidden">
      <Header />
      <Sidebar />

      {/* Main Dashboard Grid */}
      <main className="flex-1 mt-20 ml-32 mr-8 mb-32 p-8 grid grid-cols-12 grid-rows-6 gap-8 relative">
        {/* Ambient background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1000px] h-[1000px] bg-primary/5 rounded-full blur-[150px] -z-10" />

        {/* Alpha Brief — top-left */}
        <div className="col-span-3 row-span-3">
          <AlphaBrief />
        </div>

        {/* Central Neural Interaction — hero area */}
        <section className="col-span-6 col-start-4 row-span-4 flex flex-col items-center justify-center gap-16">
          <SolarOrb />
          <div className="flex gap-10 w-full justify-center">
            <NetWorth />
            <Allocation />
          </div>
        </section>

        {/* Watchlist — top-right */}
        <div className="col-span-3 col-start-10 row-span-4">
          <TerminalWatchlist />
        </div>

        {/* Risk Analysis — bottom-left */}
        <div className="col-span-3 row-start-5 row-span-2">
          <RiskAnalysis />
        </div>

        {/* Screener Picks — bottom-center */}
        <div className="col-span-6 col-start-4 row-start-5 row-span-2">
          <ScreenerPicks />
        </div>
      </main>

      <VoiceFooter />
    </div>
  );
}
