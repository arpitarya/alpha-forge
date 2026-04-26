import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

type DotTone = "live" | "warn" | "down" | "accent";

export interface LiveDotProps {
  tone?: DotTone;
  size?: number;
  pulse?: boolean;
  label?: string;
  className?: string;
}

const toneColor: Record<DotTone, string> = {
  live: "var(--green)",
  warn: "#f59e0b",
  down: "var(--red)",
  accent: "var(--accent)",
};

/**
 * Pulsing status indicator. With `label`, renders the dot + label text inline
 * (e.g. "LIVE · NSE" in the Hi-Fi top bar).
 */
export function LiveDot({
  tone = "live",
  size = 6,
  pulse = true,
  label,
  className,
}: LiveDotProps) {
  const color = toneColor[tone];
  const dot = (
    <span
      className={clsx(
        "inline-block rounded-full",
        pulse && "[animation:live-dot-pulse_2.2s_ease-in-out_infinite]",
      )}
      style={{
        width: size,
        height: size,
        background: color,
        boxShadow: `0 0 8px ${color}`,
      }}
    />
  );

  if (!label) return <span className={className}>{dot}</span>;

  return (
    <span
      className={twMerge(
        clsx(
          "inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-[color:var(--fg-3)]",
          className,
        ),
      )}
    >
      {dot}
      {label}
    </span>
  );
}
