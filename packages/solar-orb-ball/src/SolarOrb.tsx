import clsx from "clsx";
import { type CSSProperties, useId, useMemo } from "react";
import "./SolarOrb.css";

export type SolarOrbStarPreset = "constellation" | "minimal" | "none";

export interface SolarOrbProps {
  /** Diameter in px. */
  size?: number;
  /** Hex/rgb/css color for the orb's primary accent. */
  accent?: string;
  /** Lighter accent shade — used for the inner highlight gradient. */
  accentSoft?: string;
  /** Darker accent shade — used for the inner shadow rim. */
  accentDim?: string;
  /** Render the surrounding HUD frame (corner brackets + scanline + stars). */
  hud?: boolean;
  /** Star pattern around the orb. */
  starPreset?: SolarOrbStarPreset;
  /** Pulse animation in seconds (orb + outward rings). 0 disables. */
  pulseSeconds?: number;
  /** Render the two outward pulse rings. */
  rings?: boolean;
  /** Render the specular highlight on the orb's upper-left. */
  shine?: boolean;
  /** Optional caption rendered beneath the orb (e.g. status + question). */
  caption?: { eyebrow?: string; text?: string };
  className?: string;
  style?: CSSProperties;
}

/**
 * The Solar Orb. A glowing, breathing AI presence indicator.
 *
 * Rendered entirely from CSS gradients + SVG-free DOM so it scales infinitely
 * and re-tints by changing the `accent` family. Variables are scoped to the
 * component (no global pollution) — pass any color and the component computes
 * the matching glow.
 */
export function SolarOrb({
  size = 260,
  accent = "#ff8f00",
  accentSoft = "#ffb455",
  accentDim = "#c36a00",
  hud = true,
  starPreset = "constellation",
  pulseSeconds = 3.4,
  rings = true,
  shine = true,
  caption,
  className,
  style,
}: SolarOrbProps) {
  const uid = useId().replace(/:/g, "");
  const glow = useMemo(() => hexToGlow(accent), [accent]);

  const stars = STAR_PRESETS[starPreset];

  const cssVars: CSSProperties & Record<`--${string}`, string | number> = {
    "--orb-size": `${size}px`,
    "--orb-accent": accent,
    "--orb-accent-soft": accentSoft,
    "--orb-accent-dim": accentDim,
    "--orb-glow": glow,
    "--orb-pulse-duration": `${pulseSeconds}s`,
  };

  // The wrap is sized to give the HUD frame breathing room around the orb.
  const wrapSize = Math.round(size * 1.6);

  return (
    <div
      className={clsx("solar-orb-ball", className)}
      data-uid={uid}
      style={{ ...cssVars, ...style, width: wrapSize, height: wrapSize }}
    >
      {hud && (
        <>
          <span aria-hidden className="solar-orb-ball__hud solar-orb-ball__hud--tl" />
          <span aria-hidden className="solar-orb-ball__hud solar-orb-ball__hud--tr" />
          <span aria-hidden className="solar-orb-ball__hud solar-orb-ball__hud--bl" />
          <span aria-hidden className="solar-orb-ball__hud solar-orb-ball__hud--br" />
          <span aria-hidden className="solar-orb-ball__scan" />
        </>
      )}

      {stars.length > 0 && (
        <div aria-hidden className="solar-orb-ball__stars">
          {stars.map((s, i) => (
            <span
              key={`star-${i}`}
              style={{
                top: `${s.top}%`,
                ...(s.left !== undefined ? { left: `${s.left}%` } : {}),
                ...(s.right !== undefined ? { right: `${s.right}%` } : {}),
                animationDelay: `${s.delay}s`,
                background: s.accented ? "var(--orb-accent)" : undefined,
              }}
            />
          ))}
        </div>
      )}

      {rings && pulseSeconds > 0 && (
        <>
          <span aria-hidden className="solar-orb-ball__ring" />
          <span aria-hidden className="solar-orb-ball__ring solar-orb-ball__ring--delay" />
        </>
      )}

      <div
        className="solar-orb-ball__core"
        style={pulseSeconds > 0 ? undefined : { animation: "none" }}
      >
        {shine && <span aria-hidden className="solar-orb-ball__highlight" />}
      </div>

      {caption && (
        <div className="solar-orb-ball__caption">
          {caption.eyebrow && (
            <div className="solar-orb-ball__caption-eyebrow">{caption.eyebrow}</div>
          )}
          {caption.text && (
            <div className="solar-orb-ball__caption-text">{caption.text}</div>
          )}
        </div>
      )}
    </div>
  );
}

// ── helpers ─────────────────────────────────────────────────────────────

function hexToGlow(hex: string): string {
  // Convert #rrggbb (or 3-digit) to rgba with 0.18 alpha. Falls back to the
  // raw input for non-hex values so callers can pass `rgb(...)` etc.
  const m = /^#?([0-9a-f]{3,8})$/i.exec(hex.trim());
  if (!m) return hex;
  let h = m[1];
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (h.length !== 6) return hex;
  const r = Number.parseInt(h.slice(0, 2), 16);
  const g = Number.parseInt(h.slice(2, 4), 16);
  const b = Number.parseInt(h.slice(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, 0.18)`;
}

interface Star {
  top: number;
  left?: number;
  right?: number;
  delay: number;
  accented?: boolean;
}

const STAR_PRESETS: Record<SolarOrbStarPreset, Star[]> = {
  none: [],
  minimal: [
    { top: 20, left: 14, delay: 0 },
    { top: 28, right: 18, delay: 0.6, accented: true },
    { top: 70, left: 12, delay: 1.2, accented: true },
    { top: 76, right: 16, delay: 1.8 },
  ],
  constellation: [
    { top: 18, left: 14, delay: 0 },
    { top: 24, right: 18, delay: 0.6, accented: true },
    { top: 62, left: 8, delay: 1.2 },
    { top: 74, right: 12, delay: 1.8, accented: true },
    { top: 40, left: 22, delay: 2.4 },
    { top: 48, right: 24, delay: 3 },
    { top: 86, left: 36, delay: 0.3, accented: true },
    { top: 12, left: 48, delay: 1.5 },
  ],
};
