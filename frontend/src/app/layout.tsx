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
