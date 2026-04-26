import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";
import { Icon } from "./Icon";

export interface IconRailItem {
  id: string;
  /** Material symbol name. */
  icon: string;
  label?: string;
  active?: boolean;
  onClick?: () => void;
}

export interface IconRailProps {
  items: IconRailItem[];
  /** Slot rendered at the bottom (settings, profile, …). */
  footer?: ReactNode;
  width?: number;
  className?: string;
}

/**
 * Hi-Fi `.sidebar` — vertical 52px-wide rail of icon buttons. Active item
 * gets accent border + tinted bg + inner glow.
 */
export function IconRail({ items, footer, width = 52, className }: IconRailProps) {
  return (
    <aside
      style={{ width }}
      className={twMerge(
        clsx(
          "flex flex-none flex-col items-center gap-2 py-3.5",
          "rounded-[var(--radius-sm)] border border-[color:var(--line)]",
          "bg-[color:color-mix(in_srgb,var(--surface)_88%,transparent)]",
          className,
        ),
      )}
    >
      {items.map((item) => (
        <button
          key={item.id}
          type="button"
          onClick={item.onClick}
          title={item.label}
          aria-label={item.label ?? item.id}
          className={clsx(
            "grid h-10 w-10 place-items-center rounded-[var(--radius-sm)] border border-transparent transition-colors",
            item.active
              ? "border-[color:color-mix(in_srgb,var(--accent)_60%,transparent)] bg-[color:color-mix(in_srgb,var(--accent)_10%,transparent)] text-[color:var(--accent)] shadow-[inset_0_0_16px_color-mix(in_srgb,var(--accent)_16%,transparent)]"
              : "text-[color:var(--fg-3)] hover:bg-[color:color-mix(in_srgb,var(--accent)_4%,transparent)] hover:text-[color:var(--fg-2)]",
          )}
        >
          <Icon name={item.icon} size="md" />
        </button>
      ))}
      {footer && <div className="mt-auto flex flex-col items-center gap-2">{footer}</div>}
    </aside>
  );
}
