import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface VoiceDockProps {
  mic?: ReactNode;
  /** Status block — typically <Waveform/> + transcript text. */
  center?: ReactNode;
  /** Right-side action — typically a <Button variant="deploy" />. */
  cta?: ReactNode;
  className?: string;
}

/**
 * Hi-Fi `.voice` footer — surface card with a left accent stripe wrapping
 * mic + waveform + CTA.
 *
 * Layout uses a plain flex row (mic / center auto-grows / cta) instead of
 * `grid-cols-[auto_1fr_auto]` because the grid arbitrary-value form was
 * unreliable in some Tailwind v4 configurations and silently fell back to
 * vertical stacking, which broke the dock on the terminal screen.
 */
export function VoiceDock({ mic, center, cta, className }: VoiceDockProps) {
  return (
    <footer
      className={twMerge(
        clsx(
          "relative flex flex-none items-center gap-6 min-h-[80px]",
          "rounded-[var(--radius-sm)] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_82%,transparent)]",
          "px-6 py-4 backdrop-blur-md",
          "before:absolute before:left-0 before:top-0 before:h-full before:w-0.5",
          "before:bg-[linear-gradient(180deg,transparent,var(--accent),transparent)]",
          "before:opacity-50 before:content-['']",
          className,
        ),
      )}
    >
      {mic && <div className="flex flex-none items-center">{mic}</div>}
      <div className="flex min-w-0 flex-1 items-center gap-5">{center}</div>
      {cta && <div className="flex flex-none items-center">{cta}</div>}
    </footer>
  );
}
