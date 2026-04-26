import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface TreemapCellProps {
  symbol: string;
  sublabel?: string;
  value: ReactNode;
  change: ReactNode;
  /** -100..100 — drives bg tint (negative = red, positive = green). */
  pnlPct: number;
  /** Render larger sym font. */
  big?: boolean;
  /** Optional decorative right-corner element (e.g. a <Sparkline />). */
  decoration?: ReactNode;
  /** Absolute-positioning style props (left/top/width/height). */
  style?: React.CSSProperties;
  onClick?: () => void;
  className?: string;
}

/**
 * Hi-Fi `.tm-cell`. Designed to be absolutely positioned by a parent treemap
 * layout — pass `style={{ left, top, width, height }}`. Tint scales with
 * `pnlPct`: stronger sign → more saturated bg (color-mix with --green/--red).
 */
export function TreemapCell({
  symbol,
  sublabel,
  value,
  change,
  pnlPct,
  big = false,
  decoration,
  style,
  onClick,
  className,
}: TreemapCellProps) {
  // Map |pnlPct| to a 0..40% tint mix.
  const intensity = Math.min(40, Math.abs(pnlPct) * 18);
  const tone = pnlPct >= 0 ? "var(--green)" : "var(--red)";
  const bg = `color-mix(in srgb, ${tone} ${intensity}%, var(--surface))`;
  const isInteractive = !!onClick;

  return (
    <div
      onClick={onClick}
      onKeyDown={
        isInteractive
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onClick?.();
            }
          : undefined
      }
      role={isInteractive ? "button" : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      style={{ ...style, background: bg }}
      className={twMerge(
        clsx(
          "absolute flex flex-col justify-between overflow-hidden rounded-[var(--radius-sm)] p-3.5",
          "border border-[color:var(--line-hi)]",
          "transition-transform duration-300 hover:scale-[1.02] hover:z-10",
          "hover:shadow-[0_0_40px_color-mix(in_srgb,var(--accent)_25%,transparent)]",
          isInteractive && "cursor-pointer",
          className,
        ),
      )}
    >
      <div className="relative">
        <div
          className={clsx(
            "font-semibold text-[color:var(--fg)]",
            big ? "text-[22px]" : "text-base",
          )}
        >
          {symbol}
        </div>
        {sublabel && (
          <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-[color:var(--fg-3)]">
            {sublabel}
          </div>
        )}
      </div>
      {decoration && (
        <div className="absolute right-2 top-2 opacity-50">{decoration}</div>
      )}
      <div className="flex items-end justify-between">
        <div className="font-mono text-[13px] tabular-nums text-[color:var(--fg)]">
          {value}
        </div>
        <div
          className={clsx(
            "font-mono text-[11px]",
            pnlPct >= 0 ? "text-[color:var(--green)]" : "text-[color:var(--red)]",
          )}
        >
          {change}
        </div>
      </div>
    </div>
  );
}
