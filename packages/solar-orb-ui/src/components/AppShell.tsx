import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface AppShellProps {
  header?: ReactNode;
  rail?: ReactNode;
  ticker?: ReactNode;
  footer?: ReactNode;
  children: ReactNode;
  className?: string;
}

/**
 * The Hi-Fi shell. Lays out:
 *   - top header (full width)
 *   - optional ticker bar below
 *   - left icon rail
 *   - main content area (children)
 *   - bottom footer (voice dock, etc.)
 *
 * Provides the radial-gradient ambient background and uses semantic tokens so
 * a wrapping <ThemeProvider/> can flip palettes at runtime.
 */
export function AppShell({
  header,
  rail,
  ticker,
  footer,
  children,
  className,
}: AppShellProps) {
  return (
    <div
      className={twMerge(
        clsx(
          "flex h-screen w-full flex-col gap-2 overflow-hidden",
          "px-4 pt-3 pb-3",
          "bg-[color:var(--bg)]",
          "[background-image:radial-gradient(900px_600px_at_50%_40%,var(--glow),transparent_70%),radial-gradient(600px_400px_at_10%_100%,var(--glow),transparent_70%)]",
          className,
        ),
      )}
    >
      {header}
      {ticker}
      <div className="flex min-h-0 flex-1 gap-3">
        {rail}
        <main className="min-h-0 flex-1 overflow-hidden">{children}</main>
      </div>
      {footer}
    </div>
  );
}
