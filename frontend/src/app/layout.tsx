import type { Metadata } from "next";
import { QueryProvider } from "@/lib/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "Alpha Forge | Weightless Terminal",
  description:
    "AI-powered financial analysis and trading terminal for Indian markets. Institutional-grade tools for every investor.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="h-screen bg-black font-body text-on-surface antialiased selection:bg-primary/30 overflow-hidden">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
