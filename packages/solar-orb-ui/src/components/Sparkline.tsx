import { clsx } from "clsx";
import { useId } from "react";
import { twMerge } from "tailwind-merge";

type SparkTone = "up" | "dn" | "accent" | "neutral";

export interface SparklineProps {
  /** Series of y-values. Will be normalized to fit the viewBox. */
  points: number[];
  width?: number;
  height?: number;
  tone?: SparkTone;
  /** Render an area fill below the line. */
  fill?: boolean;
  /** Line stroke width. */
  strokeWidth?: number;
  className?: string;
}

const toneColor: Record<SparkTone, string> = {
  up: "var(--green)",
  dn: "var(--red)",
  accent: "var(--accent)",
  neutral: "var(--fg-3)",
};

/**
 * Compact SVG line/area chart. Used in stat cards, ledger rows, and treemap
 * cells. Pure presentational — no interactivity, no axes.
 */
export function Sparkline({
  points,
  width = 120,
  height = 28,
  tone = "accent",
  fill = false,
  strokeWidth = 1.4,
  className,
}: SparklineProps) {
  const id = useId();
  if (points.length < 2) return null;

  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const stepX = width / (points.length - 1);

  const coords = points.map((y, i) => {
    const nx = i * stepX;
    const ny = height - ((y - min) / range) * height;
    return [nx, ny] as const;
  });

  const linePath = coords
    .map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`)
    .join(" ");

  const areaPath = `${linePath} L${width},${height} L0,${height} Z`;
  const color = toneColor[tone];
  const gradId = `spark-${id}`;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="none"
      className={twMerge(clsx("block", className))}
      width={width}
      height={height}
      role="img"
      aria-hidden
    >
      {fill && (
        <>
          <defs>
            <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.5" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d={areaPath} fill={`url(#${gradId})`} />
        </>
      )}
      <path d={linePath} fill="none" stroke={color} strokeWidth={strokeWidth} />
    </svg>
  );
}
