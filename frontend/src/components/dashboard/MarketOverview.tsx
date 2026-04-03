const indices = [
  { name: "NIFTY 50", value: "—", change: "—", positive: true },
  { name: "SENSEX", value: "—", change: "—", positive: true },
  { name: "BANK NIFTY", value: "—", change: "—", positive: false },
  { name: "NIFTY IT", value: "—", change: "—", positive: true },
];

export function MarketOverview() {
  return (
    <div className="rounded border border-subtle bg-card p-3">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">
        Market Indices
      </h2>
      <div className="grid grid-cols-4 gap-3">
        {indices.map((idx) => (
          <div key={idx.name} className="rounded bg-[var(--af-bg-tertiary)] p-2">
            <p className="text-xs text-muted">{idx.name}</p>
            <p className="text-sm font-semibold">{idx.value}</p>
            <p className={`text-xs ${idx.positive ? "text-green" : "text-red"}`}>
              {idx.change}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
