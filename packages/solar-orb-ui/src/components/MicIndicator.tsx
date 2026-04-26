import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Icon } from "./Icon";

export interface MicIndicatorProps {
  size?: number;
  /** Render the double ping ring animation. */
  active?: boolean;
  className?: string;
}

/**
 * Voice-footer mic chip. Circular accent-tinted button with two staggered
 * accent rings pinging outward when `active`.
 */
export function MicIndicator({ size = 44, active = true, className }: MicIndicatorProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "relative grid place-items-center rounded-full",
          "border border-[color:var(--accent)]",
          "bg-[color:color-mix(in_srgb,var(--accent)_15%,transparent)]",
          className,
        ),
      )}
      style={{ width: size, height: size }}
    >
      {active && (
        <>
          <span
            aria-hidden
            className="absolute -inset-1 rounded-full border border-[color:var(--accent)] opacity-60 [animation:mic-ping_2s_ease-out_infinite]"
          />
          <span
            aria-hidden
            className="absolute -inset-1 rounded-full border border-[color:var(--accent)] opacity-60 [animation:mic-ping_2s_ease-out_infinite] [animation-delay:1s]"
          />
        </>
      )}
      <Icon name="mic" size="md" filled className="text-[color:var(--accent)]" />
    </div>
  );
}
