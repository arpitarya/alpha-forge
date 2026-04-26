"use client";

import { Card, Text } from "@alphaforge/solar-orb-ui";
import { useHoldings } from "@/lib/queries";

const ASSET_LABEL: Record<string, string> = {
  equity: "Equity",
  mutual_fund: "MF",
  etf: "ETF",
  bond: "Bond",
  gold: "Gold",
  crypto: "Crypto",
  cash: "Cash",
  other: "Other",
};

export function Ledger() {
  const { data, isLoading } = useHoldings();
  const holdings = data?.holdings ?? [];

  if (isLoading) {
    return (
      <Card className="flex h-full items-center justify-center">
        <Text variant="body-sm" tone="subtle">Loading ledger…</Text>
      </Card>
    );
  }

  return (
    <Card className="h-full overflow-hidden !p-0">
      <div className="h-full overflow-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead className="sticky top-0 bg-[color:var(--surface)] z-10">
            <tr>
              {["Symbol", "Source", "Class", "Qty", "Avg", "LTP", "Value", "P&L"].map((h) => (
                <th
                  key={h}
                  className="border-b border-[color:var(--line-hi)] px-4 py-3 text-right font-mono text-[10px] uppercase tracking-[0.22em] text-[color:var(--fg-3)] last:pr-6 first:text-left first:pl-6"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {holdings.map((h) => {
              const tone = h.pnl >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]";
              return (
                <tr
                  key={`${h.source}-${h.symbol}-${h.isin ?? ""}`}
                  className="border-b border-dashed border-[color:var(--line)] transition-colors hover:bg-[color:color-mix(in_srgb,var(--accent)_5%,transparent)]"
                >
                  <td className="px-6 py-3">
                    <div className="flex flex-col">
                      <span className="font-semibold">{h.symbol}</span>
                      {h.name && (
                        <span className="text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)] truncate max-w-xs">
                          {h.name}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
                    {h.source}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
                    {ASSET_LABEL[h.asset_class] ?? h.asset_class}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {h.quantity.toLocaleString("en-IN", { maximumFractionDigits: 4 })}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ₹{h.avg_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ₹{h.last_price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ₹{Math.round(h.current_value).toLocaleString("en-IN")}
                  </td>
                  <td className={`px-6 py-3 text-right tabular-nums ${tone}`}>
                    {h.pnl >= 0 ? "+" : ""}
                    ₹{Math.round(h.pnl).toLocaleString("en-IN")}{" "}
                    <span className="opacity-70 text-[11px]">
                      ({h.pnl_pct.toFixed(2)}%)
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {holdings.length === 0 && (
          <div className="p-12 text-center">
            <Text variant="body-sm" tone="subtle">
              No holdings yet — upload a broker export to populate the ledger.
            </Text>
          </div>
        )}
      </div>
    </Card>
  );
}
