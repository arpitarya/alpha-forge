import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface ProgressBarProps {
  /** Percentage value. For unidirectional: 0..100. For bidirectional: -100..100. */
  value: number;
  label?: string;
  showPercentage?: boolean;
  /**
   * Bidirectional mode — fill grows from the center. Positive values extend
   * right (accent), negative values extend left (muted). Used by the
   * rebalance rail's drift bars.
   */
  bidirectional?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  label,
  showPercentage = true,
  bidirectional = false,
  className,
}: ProgressBarProps) {
  if (bidirectional) {
    const clamped = Math.max(-100, Math.min(100, value));
    const positive = clamped >= 0;
    const width = `${Math.abs(clamped) / 2}%`;

    return (
      <div className={twMerge("flex flex-col gap-1", className)}>
        {(label || showPercentage) && (
          <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.2em] text-[color:var(--fg-3)]">
            {label && <span>{label}</span>}
            {showPercentage && (
              <span className="text-[color:var(--fg)]">
                {positive ? "+" : ""}
                {Math.round(clamped)}%
              </span>
            )}
          </div>
        )}
        <div className="relative h-[5px] w-full bg-[color:var(--line-hi)]">
          <div
            className={clsx(
              "absolute top-0 bottom-0 transition-all duration-700",
              positive
                ? "left-1/2 bg-[color:var(--accent)]"
                : "right-1/2 bg-[color:color-mix(in_srgb,var(--fg)_50%,transparent)]",
            )}
            style={{ width }}
          />
        </div>
      </div>
    );
  }

  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={twMerge("flex flex-col gap-2", className)}>
      <div className="flex items-center justify-between">
        {label && (
          <span className="font-mono text-[10px] font-bold uppercase tracking-[0.2em] text-[color:var(--accent)]">
            {label}
          </span>
        )}
        {showPercentage && (
          <span className="font-mono text-[10px] font-bold tracking-[0.15em] text-[color:var(--accent)]">
            {Math.round(clamped)}%
          </span>
        )}
      </div>
      <div className="h-1 w-full bg-[color:var(--line-hi)]">
        <div
          className="h-full bg-[linear-gradient(90deg,var(--accent),var(--accent-soft))] transition-all duration-700"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
