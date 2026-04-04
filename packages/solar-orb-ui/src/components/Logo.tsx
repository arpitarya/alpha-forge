import { clsx } from "clsx";
import { type SVGAttributes, forwardRef } from "react";
import { twMerge } from "tailwind-merge";

type LogoVariant = "full" | "icon" | "wordmark";
type LogoSize = "xs" | "sm" | "md" | "lg" | "xl";
type LogoTheme = "dark" | "light" | "auto";

export interface LogoProps extends Omit<SVGAttributes<SVGSVGElement>, "children"> {
  /** full = icon + text, icon = mark only, wordmark = text only */
  variant?: LogoVariant;
  size?: LogoSize;
  /** dark = light text (for dark bg), light = dark text (for light bg), auto = uses CSS prefers-color-scheme */
  theme?: LogoTheme;
}

/* ── Size maps ──────────────────────────────── */

const iconSizes: Record<LogoSize, number> = {
  xs: 20,
  sm: 28,
  md: 36,
  lg: 48,
  xl: 64,
};

const fullHeights: Record<LogoSize, number> = {
  xs: 20,
  sm: 28,
  md: 36,
  lg: 48,
  xl: 64,
};

// Aspect ratio of full logo is roughly 3.6:1
const fullWidths: Record<LogoSize, number> = {
  xs: 72,
  sm: 101,
  md: 130,
  lg: 173,
  xl: 230,
};

const wordmarkHeights: Record<LogoSize, number> = {
  xs: 16,
  sm: 22,
  md: 28,
  lg: 38,
  xl: 50,
};

const wordmarkWidths: Record<LogoSize, number> = {
  xs: 58,
  sm: 80,
  md: 102,
  lg: 138,
  xl: 182,
};

/* ── Icon mark (the "A" glyph with orange gradient) ── */

function LogoIcon({ size, className }: { size: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="af-grad-main" x1="32" y1="4" x2="32" y2="60" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FFB74D" />
          <stop offset="100%" stopColor="#E65100" />
        </linearGradient>
        <linearGradient id="af-grad-light" x1="28" y1="10" x2="28" y2="50" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FFCC80" />
          <stop offset="100%" stopColor="#FF8F00" />
        </linearGradient>
      </defs>
      {/* Main "A" shape — right leg */}
      <path
        d="M32 4L56 60H44L32 30L20 60H8L32 4Z"
        fill="url(#af-grad-main)"
      />
      {/* Inner lighter facet — left accent */}
      <path
        d="M22 38L32 14L38 30L28 52L22 38Z"
        fill="url(#af-grad-light)"
        opacity="0.7"
      />
      {/* Crossbar */}
      <path
        d="M20 44H44L40 36H24L20 44Z"
        fill="url(#af-grad-main)"
        opacity="0.9"
      />
    </svg>
  );
}

/* ── Wordmark ("ALPHA FORGE") ──────────────── */

function Wordmark({
  height,
  theme,
  className,
}: {
  height: number;
  theme: "dark" | "light";
  className?: string;
}) {
  const width = Math.round(height * 3.6);
  const alphaColor = theme === "dark" ? "#FFFFFF" : "#2D2D2D";
  const forgeColor = theme === "dark" ? "#9E9E9E" : "#757575";

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 260 72"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* ALPHA */}
      <text
        x="0"
        y="30"
        fill={alphaColor}
        fontFamily="'Space Grotesk', sans-serif"
        fontWeight="700"
        fontSize="32"
        letterSpacing="0.15em"
      >
        ALPHA
      </text>
      {/* FORGE */}
      <text
        x="0"
        y="62"
        fill={forgeColor}
        fontFamily="'Space Grotesk', sans-serif"
        fontWeight="400"
        fontSize="32"
        letterSpacing="0.2em"
      >
        FORGE
      </text>
    </svg>
  );
}

/* ── Main Logo component ────────────────────── */

export const Logo = forwardRef<SVGSVGElement, LogoProps>(
  ({ variant = "full", size = "md", theme = "auto", className, ...props }, ref) => {
    const resolvedTheme = theme === "auto" ? "dark" : theme;

    if (variant === "icon") {
      const s = iconSizes[size];
      return (
        <svg
          ref={ref}
          width={s}
          height={s}
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={twMerge(
            clsx(theme === "auto" && "dark:text-white text-black"),
            className,
          )}
          role="img"
          aria-label="AlphaForge"
          {...props}
        >
          <defs>
            <linearGradient id="af-icon-grad-main" x1="32" y1="4" x2="32" y2="60" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#FFB74D" />
              <stop offset="100%" stopColor="#E65100" />
            </linearGradient>
            <linearGradient id="af-icon-grad-light" x1="28" y1="10" x2="28" y2="50" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#FFCC80" />
              <stop offset="100%" stopColor="#FF8F00" />
            </linearGradient>
          </defs>
          <path d="M32 4L56 60H44L32 30L20 60H8L32 4Z" fill="url(#af-icon-grad-main)" />
          <path d="M22 38L32 14L38 30L28 52L22 38Z" fill="url(#af-icon-grad-light)" opacity="0.7" />
          <path d="M20 44H44L40 36H24L20 44Z" fill="url(#af-icon-grad-main)" opacity="0.9" />
        </svg>
      );
    }

    if (variant === "wordmark") {
      const h = wordmarkHeights[size];
      const w = wordmarkWidths[size];
      return (
        <svg
          ref={ref}
          width={w}
          height={h}
          viewBox="0 0 260 72"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={twMerge(clsx("block"), className)}
          role="img"
          aria-label="AlphaForge"
          {...props}
        >
          {theme === "auto" ? (
            <>
              {/* Dark background version (default for dark theme) */}
              <text
                x="0" y="30" fontFamily="'Space Grotesk', sans-serif"
                fontWeight="700" fontSize="32" letterSpacing="0.15em"
                className="fill-[#2D2D2D] dark:fill-white"
              >ALPHA</text>
              <text
                x="0" y="62" fontFamily="'Space Grotesk', sans-serif"
                fontWeight="400" fontSize="32" letterSpacing="0.2em"
                className="fill-[#757575] dark:fill-[#9E9E9E]"
              >FORGE</text>
            </>
          ) : (
            <>
              <text
                x="0" y="30" fill={resolvedTheme === "dark" ? "#FFFFFF" : "#2D2D2D"}
                fontFamily="'Space Grotesk', sans-serif"
                fontWeight="700" fontSize="32" letterSpacing="0.15em"
              >ALPHA</text>
              <text
                x="0" y="62" fill={resolvedTheme === "dark" ? "#9E9E9E" : "#757575"}
                fontFamily="'Space Grotesk', sans-serif"
                fontWeight="400" fontSize="32" letterSpacing="0.2em"
              >FORGE</text>
            </>
          )}
        </svg>
      );
    }

    /* ── Full logo: icon + wordmark side by side ── */
    const h = fullHeights[size];
    const w = fullWidths[size];
    const iconSize = h;

    return (
      <div
        className={twMerge(
          clsx("inline-flex items-center", `gap-[${Math.round(h * 0.2)}px]`),
          className,
        )}
        role="img"
        aria-label="AlphaForge"
      >
        <LogoIcon size={iconSize} />
        <Wordmark height={h} theme={resolvedTheme} />
      </div>
    );
  },
);

Logo.displayName = "Logo";
