const placeholderStocks = [
  { symbol: "RELIANCE", price: "—", change: "—", positive: true },
  { symbol: "TCS", price: "—", change: "—", positive: false },
  { symbol: "INFY", price: "—", change: "—", positive: true },
  { symbol: "HDFCBANK", price: "—", change: "—", positive: true },
  { symbol: "ICICIBANK", price: "—", change: "—", positive: false },
];

export function Watchlist() {
  return (
    <div className="rounded border border-subtle bg-card p-3">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
          Watchlist
        </h2>
        <button className="text-xs text-[var(--af-accent-blue)] hover:underline">+ Add</button>
      </div>
      <div className="space-y-1">
        {placeholderStocks.map((stock) => (
          <div
            key={stock.symbol}
            className="flex items-center justify-between rounded px-2 py-1.5 text-sm hover:bg-[var(--af-bg-tertiary)] cursor-pointer"
          >
            <span className="font-medium">{stock.symbol}</span>
            <div className="text-right">
              <span className="mr-3">{stock.price}</span>
              <span className={stock.positive ? "text-green" : "text-red"}>
                {stock.change}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
