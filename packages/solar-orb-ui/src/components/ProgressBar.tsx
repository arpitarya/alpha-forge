import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface ProgressBarProps {
  value: number;
  label?: string;
  showPercentage?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  label,
  showPercentage = true,
  className,
}: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={twMerge("flex flex-col gap-2", className)}>
      <div className="flex items-center justify-between">
        {label && (
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-primary">
            {label}
          </span>
        )}
        {showPercentage && (
          <span className="text-[10px] font-bold tracking-[0.15em] text-primary">
            {Math.round(clamped)}%
          </span>
        )}
      </div>
      <div className="h-1 w-full bg-surface-bright">
        <div
          className={clsx(
            "h-full bg-gradient-to-r from-primary to-primary-light transition-all duration-500",
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
