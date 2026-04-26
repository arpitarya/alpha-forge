"use client";

import {
  CountUp,
  SegmentedControl,
  Stat,
} from "@alphaforge/solar-orb-ui";
import { useHoldings } from "@/lib/queries";

export type PortfolioView = "tree" | "ledger";

export function PortfolioHeader({
  view,
  onViewChange,
}: {
  view: PortfolioView;
  onViewChange: (v: PortfolioView) => void;
}) {
  const { data } = useHoldings();
  const t = data?.totals ?? { invested: 0, current_value: 0, pnl: 0, pnl_pct: 0, count: 0 };
  const xirrPlaceholder = t.pnl_pct;

  return (
    <div className="grid grid-cols-[1.4fr_1fr_1fr_1fr_auto] gap-3">
      <Stat
        label="Total Value"
        value={<CountUp value={t.current_value} format="inr" prefix="₹" />}
        delta={`▲ ₹${Math.round(t.pnl).toLocaleString("en-IN")} · ${t.pnl_pct.toFixed(2)}% today`}
        deltaTone={t.pnl >= 0 ? "up" : "dn"}
      />
      <Stat
        label="Invested"
        value={<CountUp value={t.invested} format="inr" prefix="₹" />}
        delta={`${t.count} holdings`}
        deltaTone="neutral"
      />
      <Stat
        label="Unrealized P&L"
        value={
          <CountUp
            value={t.pnl}
            format="inr"
            prefix={t.pnl >= 0 ? "+₹" : "−₹"}
          />
        }
        delta={`${t.pnl >= 0 ? "+" : ""}${t.pnl_pct.toFixed(2)}% overall`}
        deltaTone={t.pnl >= 0 ? "up" : "dn"}
      />
      <Stat
        label="XIRR"
        value={<CountUp value={xirrPlaceholder} decimals={1} suffix="%" />}
        delta="placeholder · awaiting cashflow ledger"
        deltaTone="neutral"
      />
      <div className="self-center">
        <SegmentedControl<PortfolioView>
          options={[
            { value: "tree", label: "Treemap" },
            { value: "ledger", label: "Ledger" },
          ]}
          value={view}
          onChange={onViewChange}
        />
      </div>
    </div>
  );
}
