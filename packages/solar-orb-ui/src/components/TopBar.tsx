import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface TopBarNavItem {
  id: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

export interface TopBarProps {
  brand?: ReactNode;
  nav?: TopBarNavItem[];
  /** Right-side cluster — status pills, kbd hints, user chip. */
  right?: ReactNode;
  className?: string;
}

/**
 * Hi-Fi `.top` — branded header strip with mono-styled nav buttons. Active
 * tab gets the underline glow.
 */
export function TopBar({ brand, nav, right, className }: TopBarProps) {
  return (
    <header
      className={twMerge(
        clsx(
          "relative flex flex-none items-center justify-between gap-6",
          "rounded-[var(--radius-sm)] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)]",
          "px-4 py-2.5 backdrop-blur-md",
          "after:absolute after:inset-x-4 after:-bottom-px after:h-px",
          "after:bg-[linear-gradient(90deg,transparent,color-mix(in_srgb,var(--accent)_60%,transparent),transparent)]",
          "after:opacity-50 after:content-['']",
          className,
        ),
      )}
    >
      {brand && <div className="flex items-center gap-3.5">{brand}</div>}
      {nav && nav.length > 0 && (
        <nav className="flex items-center gap-1.5">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              disabled={item.disabled}
              onClick={item.onClick}
              className={clsx(
                "relative px-3.5 py-2 font-mono text-[10px] uppercase tracking-[0.2em] transition-colors",
                item.active
                  ? "text-[color:var(--accent)]"
                  : "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
                item.disabled && "opacity-50 cursor-not-allowed",
                item.active &&
                  "after:absolute after:inset-x-3.5 after:-bottom-[3px] after:h-0.5 after:bg-[color:var(--accent)] after:shadow-[0_0_10px_var(--glow)] after:content-['']",
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>
      )}
      {right && (
        <div className="flex items-center gap-3 font-mono text-[11px] text-[color:var(--fg-3)]">
          {right}
        </div>
      )}
    </header>
  );
}
