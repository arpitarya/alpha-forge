import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface DividerProps {
  orientation?: "horizontal" | "vertical";
  /** Use a dashed border (matches Hi-Fi watchlist row separators). */
  dashed?: boolean;
  className?: string;
}

export function Divider({
  orientation = "horizontal",
  dashed = false,
  className,
}: DividerProps) {
  // Native <hr> already has implicit role=separator + correct semantics; we
  // restyle it via border-* utilities. For vertical, we use border-l on a hr.
  const base = "border-0 m-0 p-0 bg-transparent";

  if (dashed) {
    return (
      <hr
        aria-orientation={orientation}
        className={twMerge(
          clsx(
            base,
            "border-[color:var(--line-hi)]",
            orientation === "horizontal" && "w-full border-t border-dashed",
            orientation === "vertical" && "h-full border-l border-dashed",
            className,
          ),
        )}
      />
    );
  }

  return (
    <hr
      aria-orientation={orientation}
      className={twMerge(
        clsx(
          base,
          "bg-[color:var(--line-hi)]",
          orientation === "horizontal" && "h-px w-full",
          orientation === "vertical" && "w-px h-full",
          className,
        ),
      )}
    />
  );
}
