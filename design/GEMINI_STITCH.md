# Gemini Stitch — Design Workflow for AlphaForge

> Guide for using **Google Gemini Stitch** as the primary design tool for AlphaForge.
> Covers prompt patterns, MCP integration, VS Code extension usage, and design-to-code workflow.

---

## What Is Gemini Stitch?

Gemini Stitch is Google's AI-powered UI generation tool that produces production-ready HTML/CSS/Tailwind from natural-language prompts and screenshot references. It replaces Figma as AlphaForge's design tool for rapid prototyping and component generation.

**Why Stitch over Figma:**
- Generates code directly — no manual handoff
- Understands Tailwind utility classes natively
- Accepts design-token context in prompts
- Faster iteration: prompt → preview → refine → ship

---

## MCP Server Setup

### Option A: Gemini CLI + MCP (Recommended)

Use the Gemini CLI as an MCP server so Copilot/Claude can invoke Stitch directly.

1. **Install Gemini CLI**:
   ```bash
   npm install -g @anthropic-ai/gemini-cli   # or follow Google's install guide
   ```

2. **Add to VS Code MCP config** (`.vscode/mcp.json`):
   ```json
   {
     "servers": {
       "gemini-stitch": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@anthropic-ai/gemini-cli", "stitch"],
         "env": {
           "GEMINI_API_KEY": "${env:GEMINI_API_KEY}"
         }
       }
     }
   }
   ```

3. **Set your API key**:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```

### Option B: Google AI Studio Web

Use [Google AI Studio](https://aistudio.google.com/) → Stitch mode in browser:
1. Paste the design context prompt (see below)
2. Generate the component
3. Copy the output HTML/Tailwind into the codebase
4. Convert to React component manually or with Copilot

---

## VS Code Extension Integration

### Recommended Extensions

| Extension | Purpose |
|-----------|---------|
| **Google Gemini Code Assist** | Inline AI code generation with Gemini models |
| **Gemini API Explorer** | Test Stitch prompts directly from VS Code |

### Workflow with Copilot + Stitch

1. Generate UI in Stitch (via MCP or web)
2. Paste raw HTML output into a `.stitch.html` file under `design/stitch-outputs/`
3. Use Copilot to convert to a React/Tailwind component:
   ```
   @workspace Convert design/stitch-outputs/StockCard.stitch.html
   into a React component using our Solar Terminal theme tokens
   from frontend/src/app/globals.css
   ```
4. Place the component in the appropriate `frontend/src/components/` directory

---

## Design Context Prompt

Feed this context at the start of every Stitch session to ensure brand consistency:

```
You are designing components for AlphaForge — an AI-powered trading terminal
for Indian stock markets (NSE/BSE). The design language is called "Solar Terminal":
a dark, data-dense, professional aesthetic inspired by Bloomberg Terminal meets
modern dark UI.

THEME TOKENS:
- Background primary: #0a0e17
- Background secondary: #111827
- Background card: #151d2b
- Background tertiary: #1a2332
- Border: #1e293b
- Text primary: #e2e8f0
- Text secondary: #94a3b8
- Text muted: #64748b
- Accent blue: #3b82f6
- Accent cyan: #06b6d4
- Green (profit/up): #22c55e
- Red (loss/down): #ef4444
- Orange (warning): #f59e0b
- Purple (AI features): #a855f7

TYPOGRAPHY:
- Primary font: "Space Grotesk", system-ui, sans-serif
- Mono font: "JetBrains Mono", "SF Mono", ui-monospace, monospace
- Financial numbers are ALWAYS monospace, right-aligned
- Section headers: uppercase, letter-spacing 0.05em, muted color

SPACING:
- Panel padding: 12px (compact) or 16px (standard)
- Border radius: 6px (buttons/inputs), 8px (cards/panels)
- Gap between panels: 4px

RULES:
- Use Tailwind CSS utility classes
- Positive numbers: green, prefixed with +
- Negative numbers: red, prefixed with -
- No decorative elements — every pixel earns its place
- Data density is a feature, not a bug
- Icons: Lucide icon set, 16px inline / 20px nav
```

---

## Component Generation Prompts

### Stock Ticker Row
```
Generate a stock ticker row component showing:
- Left: stock symbol (semibold) + company name (muted, truncated)
- Right: current price (mono, right-aligned) + change % (green if +, red if -)
- Hover: background changes to tertiary
- Height: 36px, horizontal padding: 8px
Use the Solar Terminal theme tokens above. Output Tailwind HTML.
```

### Market Index Card
```
Generate a market index card for NIFTY 50 showing:
- Index name (muted, 12px uppercase)
- Current value (14px, semibold, mono)
- Change value and % (12px, green/red based on direction)
- Background: tertiary, padding 8px, border-radius 8px
Use the Solar Terminal theme. Output as a grid item.
```

### AI Chat Message
```
Generate a chat message bubble for an AI financial assistant:
- AI avatar: small purple circle with sparkle icon
- Message: dark card background, 14px text, supports markdown
- Includes a disclaimer footer: "Not SEBI registered investment advice" in muted 11px
- Timestamp in caption size, right-aligned
Use Solar Terminal theme tokens.
```

### Portfolio Holdings Table
```
Generate a portfolio holdings table with columns:
Symbol | Qty | Avg Price | LTP | P&L | P&L %
- All prices in monospace, right-aligned
- P&L colored green/red based on value
- Alternating row backgrounds (card / secondary)
- Compact row height: 32px
- Header: muted uppercase 11px
Use the Solar Terminal theme. Indian stock examples: RELIANCE, TCS, INFY, HDFCBANK.
```

---

## File Organization

```
design/
├── DESIGN_SYSTEM.md          # Master design tokens & rules
├── GEMINI_STITCH.md          # This file — Stitch workflow guide
├── stitch-outputs/           # Raw Stitch HTML outputs (for reference)
│   ├── StockCard.stitch.html
│   ├── ChatBubble.stitch.html
│   └── ...
├── loading page/
│   ├── DESIGN.md
│   └── code.html
└── terminal aka landing page/
    ├── DESIGN.md
    └── code.html
```

---

## Design-to-Code Checklist

- [ ] Start Stitch session with the full design context prompt above
- [ ] Generate component HTML with realistic Indian market data
- [ ] Save raw output to `design/stitch-outputs/{ComponentName}.stitch.html`
- [ ] Convert to React + TypeScript functional component
- [ ] Replace hardcoded colors with CSS custom properties from `globals.css`
- [ ] Replace hardcoded text with props
- [ ] Add to the appropriate `frontend/src/components/` directory
- [ ] Verify dark theme contrast ratios (4.5:1 body, 3:1 large text)
- [ ] Test with realistic data lengths (long company names, large numbers)

---

## Tips

- **Iterate in Stitch first** — get the layout right before converting to React
- **Feed screenshots** — Stitch accepts reference images; screenshot existing AlphaForge pages for consistency
- **Batch similar components** — generate all card variants in one session
- **Keep the context prompt pinned** — every new Stitch chat should start with the Solar Terminal context
- **Version raw outputs** — commit `.stitch.html` files so the team can trace design decisions
