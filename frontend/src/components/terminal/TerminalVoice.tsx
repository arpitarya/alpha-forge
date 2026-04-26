"use client";

import {
  Button,
  MicIndicator,
  Text,
  VoiceDock,
  Waveform,
} from "@alphaforge/solar-orb-ui";
import { useEffect, useState } from "react";

const PROMPTS = [
  '"Alpha, analyze my exposure to AI stocks"',
  '"Show banking drag this week"',
  '"Rebalance equity down 5% to target"',
  '"Screener: breakouts under ₹500"',
];

export function TerminalVoice() {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % PROMPTS.length), 3800);
    return () => clearInterval(id);
  }, []);

  return (
    <VoiceDock
      mic={<MicIndicator size={44} active />}
      center={
        <>
          <div className="flex flex-col gap-0.5 min-w-[160px]">
            <Text className="italic text-[color:var(--accent)]">Listening…</Text>
            <Text variant="tag" tone="subtle">Neural Interface</Text>
          </div>
          <Waveform bars={8} height={24} />
          <Text className="ml-2 truncate italic text-[color:var(--fg-2)]">{PROMPTS[idx]}</Text>
        </>
      }
      cta={<Button variant="deploy" size="lg">Deploy ▸</Button>}
    />
  );
}
