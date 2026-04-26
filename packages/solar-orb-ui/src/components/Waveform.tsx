import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface WaveformProps {
  bars?: number;
  height?: number;
  /** Bar width in px. */
  barWidth?: number;
  className?: string;
}

/**
 * Faux audio meter — N accent bars that bounce on a staggered loop. Decorative
 * only (no real audio analysis); pairs with <MicIndicator /> in the voice
 * footer.
 */
export function Waveform({
  bars = 8,
  height = 24,
  barWidth = 3,
  className,
}: WaveformProps) {
  return (
    <div
      className={twMerge(clsx("flex items-center gap-[3px]", className))}
      style={{ height }}
      aria-hidden
    >
      {Array.from({ length: bars }, (_, i) => (
        <div
          key={`wbar-${i}`}
          className="bg-[color:var(--accent)] [animation:wave-bar_0.9s_ease-in-out_infinite]"
          style={{
            width: barWidth,
            height: 4,
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
      <style>{`
        @keyframes wave-bar {
          0%, 100% { height: 4px; }
          50%      { height: ${height - 2}px; }
        }
      `}</style>
    </div>
  );
}
