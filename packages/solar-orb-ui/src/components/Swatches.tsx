"use client";

import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export type AccentName = "amber" | "ion" | "signal" | "violet";

export interface SwatchesProps {
  value: AccentName;
  onChange: (next: AccentName) => void;
  className?: string;
}

const swatches: Array<{ name: AccentName; color: string; title: string }> = [
  { name: "amber", color: "#ff8f00", title: "Amber" },
  { name: "ion", color: "#2ee7c2", title: "Ion" },
  { name: "signal", color: "#ff3d5c", title: "Signal" },
  { name: "violet", color: "#a678ff", title: "Violet" },
];

/**
 * Accent picker — 4 colored circles. Active swatch gets a focus-ring outline.
 * Pair with <ThemeProvider/> to flip [data-accent] on <html>.
 */
export function Swatches({ value, onChange, className }: SwatchesProps) {
  return (
    <div className={twMerge(clsx("flex items-center gap-1.5", className))}>
      {swatches.map((s) => {
        const active = s.name === value;
        return (
          <button
            key={s.name}
            type="button"
            title={s.title}
            aria-label={s.title}
            aria-pressed={active}
            onClick={() => onChange(s.name)}
            className={clsx(
              "h-5 w-5 rounded-full border border-[color:var(--line-hi)]",
              active && "outline outline-2 outline-[color:var(--fg)] outline-offset-2",
            )}
            style={{ background: s.color }}
          />
        );
      })}
    </div>
  );
}
