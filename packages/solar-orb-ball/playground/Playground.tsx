import { useState } from "react";
import { SolarOrb, type SolarOrbStarPreset } from "../src";
import "./playground.css";

const PRESETS: Array<{ name: string; accent: string; soft: string; dim: string }> = [
  { name: "Amber", accent: "#ff8f00", soft: "#ffb455", dim: "#c36a00" },
  { name: "Ion", accent: "#2ee7c2", soft: "#79f2d8", dim: "#0f9e85" },
  { name: "Signal", accent: "#ff3d5c", soft: "#ff7185", dim: "#b80026" },
  { name: "Violet", accent: "#a678ff", soft: "#c6a6ff", dim: "#6a3fc7" },
];

const STAR_OPTIONS: SolarOrbStarPreset[] = ["constellation", "minimal", "none"];

export function Playground() {
  const [presetIdx, setPresetIdx] = useState(0);
  const [size, setSize] = useState(260);
  const [pulseSeconds, setPulseSeconds] = useState(3.4);
  const [hud, setHud] = useState(true);
  const [rings, setRings] = useState(true);
  const [starPreset, setStarPreset] = useState<SolarOrbStarPreset>("constellation");
  const [bg, setBg] = useState("#000000");
  const [showCaption, setShowCaption] = useState(true);

  const preset = PRESETS[presetIdx];

  return (
    <div className="pg" style={{ background: bg }}>
      <header className="pg-header">
        <div className="pg-brand">⊙ solar-orb-ball</div>
        <div className="pg-meta">playground · {process.env.NODE_ENV ?? "dev"}</div>
      </header>

      <main className="pg-stage">
        <SolarOrb
          size={size}
          accent={preset.accent}
          accentSoft={preset.soft}
          accentDim={preset.dim}
          hud={hud}
          rings={rings}
          starPreset={starPreset}
          pulseSeconds={pulseSeconds}
          caption={
            showCaption
              ? { eyebrow: "· READY · SPEAK WHEN YOU LIKE", text: "What's moving my portfolio today?" }
              : undefined
          }
        />
      </main>

      <aside className="pg-panel">
        <section>
          <h3>Accent</h3>
          <div className="pg-swatch-row">
            {PRESETS.map((p, i) => (
              <button
                key={p.name}
                type="button"
                className={`pg-swatch ${i === presetIdx ? "is-active" : ""}`}
                onClick={() => setPresetIdx(i)}
                style={{ background: p.accent }}
                title={p.name}
                aria-label={p.name}
              />
            ))}
          </div>
        </section>

        <section>
          <h3>Size · {size}px</h3>
          <input
            type="range"
            min={120}
            max={520}
            step={4}
            value={size}
            onChange={(e) => setSize(Number(e.target.value))}
          />
        </section>

        <section>
          <h3>Pulse · {pulseSeconds.toFixed(1)}s</h3>
          <input
            type="range"
            min={0}
            max={8}
            step={0.1}
            value={pulseSeconds}
            onChange={(e) => setPulseSeconds(Number(e.target.value))}
          />
        </section>

        <section>
          <h3>Stars</h3>
          <div className="pg-segment">
            {STAR_OPTIONS.map((o) => (
              <button
                key={o}
                type="button"
                className={`pg-seg-btn ${starPreset === o ? "is-active" : ""}`}
                onClick={() => setStarPreset(o)}
              >
                {o}
              </button>
            ))}
          </div>
        </section>

        <section className="pg-toggles">
          <label>
            <input type="checkbox" checked={hud} onChange={(e) => setHud(e.target.checked)} />
            HUD corners + scanline
          </label>
          <label>
            <input
              type="checkbox"
              checked={rings}
              onChange={(e) => setRings(e.target.checked)}
            />
            Pulse rings
          </label>
          <label>
            <input
              type="checkbox"
              checked={showCaption}
              onChange={(e) => setShowCaption(e.target.checked)}
            />
            Caption
          </label>
        </section>

        <section>
          <h3>Background</h3>
          <input type="color" value={bg} onChange={(e) => setBg(e.target.value)} />
        </section>
      </aside>
    </div>
  );
}
