import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { MarketOverview } from "@/components/dashboard/MarketOverview";
import { AIChat } from "@/components/ai/AIChat";
import { Watchlist } from "@/components/dashboard/Watchlist";

export default function Home() {
  return (
    <div className="flex h-screen flex-col">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex flex-1 gap-1 overflow-hidden p-1">
          {/* Left panel: Market Overview + Chart */}
          <div className="flex flex-[2] flex-col gap-1">
            <MarketOverview />
            <div className="flex-1 rounded border border-subtle bg-card p-4">
              <p className="text-muted text-sm">
                Chart — select a symbol to view price action
              </p>
            </div>
          </div>

          {/* Right panel: Watchlist + AI Chat */}
          <div className="flex w-96 flex-col gap-1">
            <Watchlist />
            <AIChat />
          </div>
        </main>
      </div>
    </div>
  );
}
