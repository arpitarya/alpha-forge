"use client";

import { Card, Text } from "@alphaforge/solar-orb-ui";
import { LedgerRow } from "./LedgerRow";
import { LEDGER_HEADERS } from "./ledger.utils";
import { useHoldings } from "./portfolio.query";

export function Ledger() {
  const { data, isLoading } = useHoldings();
  const holdings = data?.holdings ?? [];

  if (isLoading) {
    return (
      <Card className="flex h-full items-center justify-center">
        <Text variant="body-sm" tone="subtle">
          Loading ledger…
        </Text>
      </Card>
    );
  }

  return (
    <Card className="h-full overflow-hidden !p-0">
      <div className="h-full overflow-auto">
        <table className="w-full border-collapse text-[13px]">
          <thead className="sticky top-0 bg-[color:var(--surface)] z-10">
            <tr>
              {LEDGER_HEADERS.map((h) => (
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
            {holdings.map((h) => (
              <LedgerRow key={`${h.source}-${h.symbol}-${h.isin ?? ""}`} h={h} />
            ))}
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
