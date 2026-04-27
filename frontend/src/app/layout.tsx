import { ThemeProvider } from "@alphaforge/solar-orb-ui";
import type { Metadata } from "next";
import { QueryProvider } from "@/lib/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "AlphaForge | Personal Investment Terminal",
  description:
    "Personal AI-powered portfolio management & investment terminal for Indian markets.",
};

// Pre-hydration script: read persisted theme/accent from localStorage and set
// the data-attrs before React hydrates. Prevents the dark→light flash during
// initial paint when the user has previously toggled the theme.
const themeBootstrap = `
(function () {
  try {
    var raw = localStorage.getItem('solar-orb-theme');
    var s = raw ? JSON.parse(raw) : {};
    var html = document.documentElement;
    html.dataset.theme = s.theme || 'dark';
    html.dataset.accent = s.accent || 'amber';
  } catch (e) {
    document.documentElement.dataset.theme = 'dark';
    document.documentElement.dataset.accent = 'amber';
  }
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark" data-accent="amber">
      <head>
        {/*
          Font preconnects + stylesheet links. Loading the icon font via <link>
          (rather than @import inside CSS) makes it parallel-discovered and
          prevents the "icon name renders as raw text" flash that happens when
          the @import URL hasn't resolved by first paint.
        */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap"
        />
        {/*
          Material Symbols intentionally uses display=block (not swap). With
          swap, the fallback would render icon NAMES as plain text until the
          font loads — that's exactly the "balance_wallet / mic / forum"
          glyph-as-text bug we just fixed. Block holds the slot blank until
          the icon font is ready.
        */}
        {/* eslint-disable-next-line @next/next/google-font-display */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block"
        />
        {/* biome-ignore lint/security/noDangerouslySetInnerHtml: pre-hydration script must be inlined to run before React hydrates and prevent theme-flash */}
        <script dangerouslySetInnerHTML={{ __html: themeBootstrap }} />
      </head>
      <body className="h-screen overflow-hidden bg-black font-body text-on-surface antialiased selection:bg-primary/30">
        <ThemeProvider>
          <QueryProvider>{children}</QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
