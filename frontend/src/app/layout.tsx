import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AlphaForge — AI-Powered Trading Terminal",
  description:
    "Institutional-grade financial analysis and trading platform powered by AI. Built for Indian markets.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
