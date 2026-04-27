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
 * Hi-Fi `.top` — branded header strip with nav buttons.
 *
 * Nav buttons use a comfortable click target (44px tall, 11px font) so the
 * header is keyboard- and pointer-friendly without dwarfing the rest of the
 * chrome. Active tab gets the underline glow.
 */
export function TopBar({ brand, nav, right, className }: TopBarProps) {
  return (
    <header
      className={twMerge(
        clsx(
          "relative flex flex-none items-center justify-between gap-6",
          "rounded-[var(--radius-sm)] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)]",
          "px-5 py-3 backdrop-blur-md",
          "after:absolute after:inset-x-5 after:-bottom-px after:h-px",
          "after:bg-[linear-gradient(90deg,transparent,color-mix(in_srgb,var(--accent)_60%,transparent),transparent)]",
          "after:opacity-50 after:content-['']",
          className,
        ),
      )}
    >
      {brand && <div className="flex items-center gap-3.5">{brand}</div>}
      {nav && nav.length > 0 && (
        <nav className="flex items-center gap-1">
          {nav.map((item) => (
            <button
              key={item.id}
              type="button"
              disabled={item.disabled}
              onClick={item.onClick}
              className={clsx(
                "relative inline-flex h-10 items-center justify-center rounded-[var(--radius-sm)]",
                "px-5 font-mono text-[11px] uppercase tracking-[0.22em] transition-colors",
                "min-w-[110px]",
                item.active
                  ? "text-[color:var(--accent)] bg-[color:color-mix(in_srgb,var(--accent)_8%,transparent)]"
                  : "text-[color:var(--fg-3)] hover:text-[color:var(--fg)] hover:bg-[color:color-mix(in_srgb,var(--accent)_4%,transparent)]",
                item.disabled && "opacity-50 cursor-not-allowed",
                item.active &&
                  "after:absolute after:inset-x-3 after:-bottom-1 after:h-0.5 after:bg-[color:var(--accent)] after:shadow-[0_0_10px_var(--glow)] after:content-['']",
              )}
            >
              {item.label}
            </button>
          ))}
        </nav>
      )}
      {right && (
        <div className="flex items-center gap-4 font-mono text-[11px] text-[color:var(--fg-3)]">
          {right}
        </div>
      )}
    </header>
  );
}
