import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export type BootStepState = "queued" | "now" | "ok";

export interface BootStepProps {
  label: string;
  status: string;
  state: BootStepState;
  className?: string;
}

const stateGlyph: Record<BootStepState, string> = {
  queued: "○",
  now: "◐",
  ok: "✓",
};

/**
 * One row in the boot screen list. State `now` spins; `ok` shows green; `queued`
 * dimmed. Compose multiple rows with <ProgressBar /> to recreate the Hi-Fi
 * loading screen.
 */
export function BootStep({ label, status, state, className }: BootStepProps) {
  return (
    <li
      className={twMerge(
        clsx(
          "grid grid-cols-[18px_1fr_auto] items-center gap-3.5 font-mono text-[12.5px] transition-colors",
          state === "queued" && "text-[color:var(--fg-3)]",
          state === "now" && "text-[color:var(--fg)]",
          state === "ok" && "text-[color:var(--fg)]",
          className,
        ),
      )}
    >
      <span
        className={clsx(
          "grid h-[18px] w-[18px] place-items-center text-sm",
          state === "ok" && "text-[color:var(--green)]",
          state === "now" &&
            "text-[color:var(--accent)] [animation:boot-spin_1.4s_linear_infinite]",
        )}
      >
        {stateGlyph[state]}
      </span>
      <span>{label}</span>
      <span
        className={clsx(
          "text-[11px] uppercase tracking-[0.18em]",
          state === "now" ? "text-[color:var(--accent)]" : "text-[color:var(--fg-3)]",
        )}
      >
        {status}
      </span>
      <style>{`@keyframes boot-spin { to { transform: rotate(1turn); } }`}</style>
    </li>
  );
}
