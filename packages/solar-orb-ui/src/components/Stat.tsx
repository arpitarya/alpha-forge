import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";
import { Sparkline, type SparklineProps } from "./Sparkline";

type StatTone = "up" | "dn" | "neutral" | "accent";

export interface StatProps {
  label: string;
  /** Headline value — pass <CountUp/> for animated numbers, or any node. */
  value: ReactNode;
  /** Smaller line beneath the value (e.g. "+1.24% TODAY · +₹1,52,330"). */
  delta?: ReactNode;
  deltaTone?: StatTone;
  /** Optional sparkline rendered along the bottom of the card. */
  sparkline?: SparklineProps;
  /** Show Hi-Fi top-left accent corner ticks. */
  corner?: boolean;
  className?: string;
}

const deltaToneClass: Record<StatTone, string> = {
  up: "text-[color:var(--green)]",
  dn: "text-[color:var(--red)]",
  neutral: "text-[color:var(--fg-3)]",
  accent: "text-[color:var(--accent)]",
};

/**
 * Hi-Fi `.stat` card. Label · large value · optional delta · optional
 * sparkline. The L-shaped corner mark is the accent-tinted hairline from the
 * `::before/::after` decoration in the source.
 */
export function Stat({
  label,
  value,
  delta,
  deltaTone = "neutral",
  sparkline,
  corner = true,
  className,
}: StatProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "relative overflow-hidden rounded-[var(--radius-md)] p-5",
          "bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)]",
          "border border-[color:var(--line)]",
          className,
        ),
      )}
    >
      {corner && (
        <>
          <span
            aria-hidden
            className="absolute left-0 top-0 h-px w-6 bg-[color:var(--accent)] opacity-60"
          />
          <span
            aria-hidden
            className="absolute left-0 top-0 h-6 w-px bg-[color:var(--accent)] opacity-60"
          />
        </>
      )}
      <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-[color:var(--fg-3)]">
        {label}
      </div>
      <div className="mt-1.5 text-3xl font-medium tracking-[-0.02em] text-[color:var(--fg)] tabular-nums">
        {value}
      </div>
      {delta && (
        <div className={clsx("mt-0.5 font-mono text-[11px]", deltaToneClass[deltaTone])}>
          {delta}
        </div>
      )}
      {sparkline && (
        <div className="absolute inset-x-0 bottom-0 h-10 w-full opacity-60">
          <Sparkline {...sparkline} width={400} height={40} />
        </div>
      )}
    </div>
  );
}
