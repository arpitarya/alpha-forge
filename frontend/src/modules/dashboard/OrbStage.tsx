"use client";

import { SolarOrb } from "@alphaforge/solar-orb-ball";
import { useEffect, useState } from "react";

const QUESTIONS = [
  "What's moving my portfolio today?",
  "How exposed am I to IT?",
  "Show screener picks with confidence > 0.8",
  "Rebalance my equity to target",
  "Compare HDFCBANK vs ICICIBANK this quarter",
];

export function OrbStage() {
  const [questionIdx, setQuestionIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setQuestionIdx((i) => (i + 1) % QUESTIONS.length);
    }, 4500);
    return () => clearInterval(id);
  }, []);

  return (
    <div
      className="relative flex h-full items-center justify-center overflow-hidden rounded-[var(--radius-md)] border border-[color:var(--line)]"
      style={{
        background:
          "radial-gradient(80% 70% at 50% 50%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 70%), color-mix(in srgb, var(--surface) 50%, transparent)",
      }}
    >
      <SolarOrb
        size={260}
        accent="var(--accent)"
        accentSoft="var(--accent-soft)"
        accentDim="var(--accent-dim)"
        caption={{
          eyebrow: "· READY · SPEAK WHEN YOU LIKE",
          text: QUESTIONS[questionIdx],
        }}
      />
    </div>
  );
}
