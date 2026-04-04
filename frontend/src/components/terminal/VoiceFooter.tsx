"use client";

import { useState } from "react";

export function VoiceFooter() {
  const [input, setInput] = useState("");

  return (
    <footer className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[calc(100%-48px)] max-w-7xl z-50 h-24 floating-shard rounded-full flex items-center px-12 gap-12">
      {/* Mic button */}
      <div className="flex items-center gap-6">
        <div className="relative w-12 h-12 flex items-center justify-center">
          <div className="absolute inset-0 bg-primary/20 rounded-full animate-ping opacity-20" />
          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center border border-primary/20">
            <span
              className="material-symbols-outlined text-primary"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              mic
            </span>
          </div>
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-bold italic text-primary/80 animate-pulse uppercase tracking-wider">
            Listening...
          </span>
          <span className="text-[8px] font-bold text-white/20 uppercase tracking-[0.4em]">
            Neural Interface
          </span>
        </div>
      </div>

      {/* Waveform */}
      <div className="flex-1 h-8 flex items-center gap-1.5 opacity-40">
        {[3, 6, 4, 7, 5, 2].map((h) => (
          <div
            key={`bar-${h}`}
            className="w-1 bg-primary rounded-full animate-bounce"
            style={{
              height: `${h * 4}px`,
              animationDelay: `${h * 0.05}s`,
            }}
          />
        ))}
      </div>

      {/* Text input */}
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={`"Alpha, analyze the exposure to AI stocks in my equity portfolio..."`}
        className="flex-1 bg-transparent text-white/40 text-sm font-light italic tracking-wide outline-none placeholder:text-white/40 max-w-md truncate"
      />

      {/* Deploy button */}
      <button className="bg-primary hover:brightness-110 text-black font-bold text-[10px] uppercase tracking-[0.2em] px-8 py-3 rounded-full transition-transform hover:scale-105 active:scale-95 shadow-lg shadow-primary/20">
        Deploy
      </button>
    </footer>
  );
}
