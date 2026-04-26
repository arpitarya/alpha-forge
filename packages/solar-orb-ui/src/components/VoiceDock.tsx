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
 * Hi-Fi `.voice` footer — surface card with a left accent stripe (the
 * `::before` accent gradient) wrapping mic + waveform + CTA.
 */
export function VoiceDock({ mic, center, cta, className }: VoiceDockProps) {
  return (
    <footer
      className={twMerge(
        clsx(
          "relative grid grid-cols-[auto_1fr_auto] items-center gap-5",
          "rounded-[var(--radius-sm)] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_82%,transparent)]",
          "px-5 py-4 backdrop-blur-md",
          "before:absolute before:left-0 before:top-0 before:h-full before:w-0.5",
          "before:bg-[linear-gradient(180deg,transparent,var(--accent),transparent)]",
          "before:opacity-50 before:content-['']",
          className,
        ),
      )}
    >
      {mic}
      <div className="flex min-w-0 items-center gap-4">{center}</div>
      {cta}
    </footer>
  );
}
