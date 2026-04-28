"use client";

import type { HoldingDTO } from "./portfolio.types";
import { ASSET_LABEL } from "./ledger.utils";

export function LedgerRow({ h }: { h: HoldingDTO }) {
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
      <td className="px-4 py-3 text-right tabular-nums">₹{h.avg_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-right tabular-nums">₹{h.last_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-right tabular-nums">
        ₹{Math.round(h.current_value).toLocaleString("en-IN")}
      </td>
      <td className={`px-6 py-3 text-right tabular-nums ${tone}`}>
        {h.pnl >= 0 ? "+" : ""}₹{Math.round(h.pnl).toLocaleString("en-IN")}{" "}
        <span className="opacity-70 text-[11px]">({h.pnl_pct.toFixed(2)}%)</span>
      </td>
    </tr>
  );
}
