import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface RiskBarsProps {
  /** Bar heights as percentages 0..100. */
  values: number[];
  /** Index of the bar to highlight with the accent glow. */
  activeIndex?: number;
  /** Container height in px. */
  height?: number;
  className?: string;
}

/**
 * Hi-Fi `.risk .bars` — a strip of vertical fills with one accent-glowing
 * bar. Used in the watchlist card to show a confidence histogram.
 */
export function RiskBars({
  values,
  activeIndex,
  height = 64,
  className,
}: RiskBarsProps) {
  return (
    <div
      className={twMerge(clsx("flex items-stretch gap-1.5", className))}
      style={{ height }}
    >
      {values.map((v, i) => {
        const active = i === activeIndex;
        const pct = Math.max(0, Math.min(100, v));
        return (
          <div
            key={`${i}-${v}`}
            className="relative flex-1 overflow-hidden bg-[color:var(--line-hi)]"
          >
            <div
              className={clsx(
                "absolute inset-x-0 bottom-0 transition-[height] duration-700",
                active
                  ? "bg-[color:var(--accent)] shadow-[0_0_22px_var(--glow)]"
                  : "bg-[color:var(--fg-4)]",
              )}
              style={{ height: `${pct}%` }}
            />
          </div>
        );
      })}
    </div>
  );
}
