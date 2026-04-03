"use client";

import { useState } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to AlphaForge AI. Ask me about any stock, get portfolio insights, or request trade analysis. Try: \"Analyze RELIANCE\" or \"What are the best momentum stocks today?\"",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // TODO: call /api/v1/ai/chat
    const assistantMessage: Message = {
      role: "assistant",
      content: "AI service is not yet connected. This will provide real-time market analysis and trade recommendations.",
    };
    setMessages((prev) => [...prev, assistantMessage]);
  };

  return (
    <div className="flex flex-1 flex-col rounded border border-subtle bg-card">
      <div className="border-b border-subtle p-2">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
          🤖 AI Assistant
        </h2>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded p-2 text-xs leading-relaxed ${
              msg.role === "user"
                ? "ml-8 bg-[var(--af-accent-blue)]/20 text-[var(--af-text-primary)]"
                : "mr-8 bg-[var(--af-bg-tertiary)] text-[var(--af-text-secondary)]"
            }`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <div className="border-t border-subtle p-2">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask AlphaForge AI..."
            className="flex-1 rounded bg-[var(--af-bg-tertiary)] px-3 py-1.5 text-xs text-[var(--af-text-primary)] placeholder-[var(--af-text-muted)] outline-none focus:ring-1 focus:ring-[var(--af-accent-blue)]"
          />
          <button
            onClick={handleSend}
            className="rounded bg-[var(--af-accent-blue)] px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-600"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
