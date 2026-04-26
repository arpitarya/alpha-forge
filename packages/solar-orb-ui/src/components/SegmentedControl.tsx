"use client";

import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface SegmentedOption<T extends string = string> {
  value: T;
  label: string;
}

export interface SegmentedControlProps<T extends string = string> {
  options: SegmentedOption<T>[];
  value: T;
  onChange: (next: T) => void;
  className?: string;
}

/**
 * Hi-Fi `.seg` — bordered button group; active segment fills with accent.
 * Used for the theme switcher (Dark/Light) and the portfolio Treemap/Ledger
 * toggle.
 */
export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  className,
}: SegmentedControlProps<T>) {
  return (
    <div
      role="radiogroup"
      className={twMerge(
        clsx(
          "inline-flex border border-[color:var(--line)] bg-[color:var(--surface)]",
          className,
        ),
      )}
    >
      {options.map((opt, i) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            role="radio"
            type="button"
            aria-checked={active}
            onClick={() => onChange(opt.value)}
            className={clsx(
              "px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.18em] transition-colors",
              i < options.length - 1 && "border-r border-[color:var(--line)]",
              active
                ? "bg-[color:var(--accent)] text-[color:var(--on-accent)]"
                : "text-[color:var(--fg-3)] hover:text-[color:var(--fg-2)]",
            )}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
