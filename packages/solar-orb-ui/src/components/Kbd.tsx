import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface KbdProps {
  children: ReactNode;
  className?: string;
}

/**
 * Inline keyboard hint, e.g. ⌘K. Matches Hi-Fi `.kbd`.
 */
export function Kbd({ children, className }: KbdProps) {
  return (
    <kbd
      className={twMerge(
        clsx(
          "inline-flex items-center font-mono text-[10px] px-1.5 py-0.5",
          "border border-[color:var(--line-hi)] text-[color:var(--fg-2)]",
          "rounded-[var(--radius-sm)] bg-transparent",
          className,
        ),
      )}
    >
      {children}
    </kbd>
  );
}
