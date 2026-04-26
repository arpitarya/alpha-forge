import { clsx } from "clsx";
import type { ReactNode } from "react";
import { twMerge } from "tailwind-merge";

export interface HudCornersProps {
  children?: ReactNode;
  /** Hide individual corners (default: all 4 shown). */
  corners?: { tl?: boolean; tr?: boolean; bl?: boolean; br?: boolean };
  className?: string;
}

/**
 * Wraps content with 4 absolutely-positioned accent corner brackets — the
 * "scanner frame" decoration around the orb stage, treemap, and boot screen
 * in the Hi-Fi mock.
 *
 * Make sure the parent has `position: relative` (this component sets it).
 */
export function HudCorners({
  children,
  corners = { tl: true, tr: true, bl: true, br: true },
  className,
}: HudCornersProps) {
  return (
    <div className={twMerge(clsx("relative", className))}>
      {children}
      {corners.tl && <span aria-hidden className="hud-corner tl" />}
      {corners.tr && <span aria-hidden className="hud-corner tr" />}
      {corners.bl && <span aria-hidden className="hud-corner bl" />}
      {corners.br && <span aria-hidden className="hud-corner br" />}
    </div>
  );
}
