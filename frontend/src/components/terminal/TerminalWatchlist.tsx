const watchlistItems = [
  {
    symbol: "BTC",
    name: "Bitcoin",
    icon: "currency_bitcoin",
    price: "$64,281",
    change: "+2.4%",
    positive: true,
  },
  {
    symbol: "NVDA",
    name: "Nvidia",
    icon: "memory",
    price: "$894.20",
    change: "+1.8%",
    positive: true,
  },
  {
    symbol: "SOL",
    name: "Solana",
    icon: "auto_awesome",
    price: "$142.15",
    change: "-0.9%",
    positive: false,
  },
];

export function TerminalWatchlist() {
  return (
    <section className="h-full floating-shard rounded-[2.5rem] p-10 flex flex-col gap-8">
      <div className="flex justify-between items-center">
        <h2 className="text-sm font-bold tracking-[0.3em] uppercase text-white/90">Watchlist</h2>
        <span className="material-symbols-outlined text-white/20 hover:text-white transition-colors cursor-pointer">
          add
        </span>
      </div>
      <div className="space-y-10">
        {watchlistItems.map((item) => (
          <div key={item.symbol} className="flex items-center justify-between group cursor-pointer">
            <div className="flex gap-4 items-center">
              <div className="w-10 h-10 rounded-2xl bg-white/5 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <span className="material-symbols-outlined text-primary text-sm">{item.icon}</span>
              </div>
              <div>
                <p className="font-bold text-sm tracking-tight">{item.symbol}</p>
                <p className="text-[10px] text-white/30 uppercase tracking-tighter">{item.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-sm">{item.price}</p>
              <p
                className={`text-[10px] font-bold ${
                  item.positive ? "text-emerald-400" : "text-red-400/80"
                }`}
              >
                {item.change}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
