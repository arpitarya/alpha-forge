import type { Metadata } from "next";
import { QueryProvider } from "@/lib/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "AlphaForge | Personal Investment Terminal",
  description:
    "Personal AI-powered portfolio management & investment terminal for Indian markets.",
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
