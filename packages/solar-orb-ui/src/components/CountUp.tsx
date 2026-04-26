"use client";

import { clsx } from "clsx";
import { useEffect, useRef, useState } from "react";
import { twMerge } from "tailwind-merge";

type CountFormat = "inr" | "usd" | "plain" | "pct";

export interface CountUpProps {
  value: number;
  format?: CountFormat;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  /** Animation duration in ms. Set 0 to disable. */
  duration?: number;
  className?: string;
}

/**
 * Indian-grouping (12,84,500) when format=inr; standard locale otherwise.
 */
function formatNumber(value: number, format: CountFormat, decimals: number): string {
  if (format === "inr") {
    const int = Math.round(value);
    const s = int.toString();
    const lastThree = s.slice(-3);
    const other = s.slice(0, -3);
    return (other ? `${other.replace(/\B(?=(\d{2})+(?!\d))/g, ",")},` : "") + lastThree;
  }
  if (format === "pct") return `${value.toFixed(decimals)}`;
  if (decimals > 0) return value.toFixed(decimals);
  return Math.round(value).toLocaleString();
}

/**
 * Animated counter that eases up to `value`. Re-animates when `value` changes.
 * Hi-Fi terminal stat cards use this for the headline numbers.
 */
export function CountUp({
  value,
  format = "plain",
  decimals = 0,
  prefix = "",
  suffix = "",
  duration = 1400,
  className,
}: CountUpProps) {
  const [display, setDisplay] = useState(value);
  const fromRef = useRef(0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (duration <= 0) {
      setDisplay(value);
      return;
    }
    const start = performance.now();
    const from = fromRef.current;
    const target = value;

    const step = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - (1 - t) ** 3;
      setDisplay(from + (target - from) * eased);
      if (t < 1) {
        rafRef.current = requestAnimationFrame(step);
      } else {
        fromRef.current = target;
      }
    };
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, [value, duration]);

  return (
    <span className={twMerge(clsx("tabular-nums", className))}>
      {prefix}
      {formatNumber(display, format, decimals)}
      {suffix}
    </span>
  );
}
