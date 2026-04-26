"use client";

import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface TickerItem {
  symbol: string;
  price: string;
  change: string;
  tone?: "up" | "dn";
}

export interface TickerProps {
  items: TickerItem[];
  /** Loop duration in seconds. Lower = faster scroll. */
  speedSeconds?: number;
  className?: string;
}

/**
 * Horizontal scrolling marquee. Duplicates the item list inline so the CSS
 * animation can translate -50% for a seamless loop. Pure CSS — no JS timer.
 */
export function Ticker({ items, speedSeconds = 48, className }: TickerProps) {
  const renderRun = (keySalt: string) =>
    items.map((it, i) => (
      <span
        key={`${keySalt}-${it.symbol}-${i}`}
        className="inline-flex items-center gap-2"
      >
        <b className="text-[color:var(--fg)]">{it.symbol}</b>
        <span className="font-mono text-[color:var(--fg-2)]">{it.price}</span>
        <span
          className={clsx(
            "font-mono",
            it.tone === "dn" ? "text-[color:var(--red)]" : "text-[color:var(--green)]",
          )}
        >
          {it.change}
        </span>
        <span className="px-2 text-[color:var(--fg-3)]/40">·</span>
      </span>
    ));

  return (
    <div
      className={twMerge(
        clsx(
          "relative flex h-7 items-center overflow-hidden rounded-[var(--radius-sm)]",
          "border border-[color:var(--line)] bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)]",
          "px-4 font-mono text-[11px] text-[color:var(--fg-2)] whitespace-nowrap",
          className,
        ),
      )}
    >
      <div
        className="flex gap-9 [animation-name:ticker-slide] [animation-timing-function:linear] [animation-iteration-count:infinite]"
        style={{ animationDuration: `${speedSeconds}s` }}
      >
        {renderRun("a")}
        {renderRun("b")}
      </div>
      <style>{`
        @keyframes ticker-slide {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  );
}
