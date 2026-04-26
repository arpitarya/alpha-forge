import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface WatchRowProps {
  symbol: string;
  /** Sub-label (exchange · sector). */
  sublabel?: string;
  /** Single character or short string rendered in the icon square. */
  icon?: ReactNode;
  price: ReactNode;
  change: ReactNode;
  changeTone?: "up" | "dn";
  onClick?: () => void;
  className?: string;
}

/**
 * Hi-Fi `.watch .row` — icon · symbol+sub · price · change.
 * Icon square uses Space Mono caps to match the mock; pass a Material Icon
 * via children if you need glyphs.
 */
export function WatchRow({
  symbol,
  sublabel,
  icon,
  price,
  change,
  changeTone = "up",
  onClick,
  className,
}: WatchRowProps) {
  const isInteractive = !!onClick;
  const Tag = isInteractive ? "button" : "div";

  return (
    <Tag
      type={isInteractive ? "button" : undefined}
      onClick={onClick}
      className={twMerge(
        clsx(
          "grid grid-cols-[28px_1fr_auto_auto] items-center gap-2.5 py-1.5 text-left",
          "transition-colors hover:bg-[color:color-mix(in_srgb,var(--accent)_6%,transparent)]",
          isInteractive && "cursor-pointer",
          className,
        ),
      )}
    >
      <div className="grid h-7 w-7 place-items-center border border-[color:var(--line-hi)] font-mono text-[10px] text-[color:var(--fg-2)]">
        {icon ?? symbol[0]}
      </div>
      <div className="min-w-0">
        <div className="truncate text-[13px] font-semibold tracking-[0.01em] text-[color:var(--fg)]">
          {symbol}
        </div>
        {sublabel && (
          <div className="truncate font-mono text-[10px] uppercase tracking-[0.14em] text-[color:var(--fg-3)]">
            {sublabel}
          </div>
        )}
      </div>
      <div className="text-right text-[13px] tabular-nums text-[color:var(--fg)]">{price}</div>
      <div
        className={clsx(
          "w-14 text-right font-mono text-[10px] tabular-nums",
          changeTone === "up"
            ? "text-[color:var(--green)]"
            : "text-[color:var(--red)]",
        )}
      >
        {change}
      </div>
    </Tag>
  );
}
