"use client";

import { Kbd, LiveDot, TopBar, type TopBarNavItem } from "@alphaforge/solar-orb-ui";
import { usePathname, useRouter } from "next/navigation";

const NAV_ITEMS: Array<{ id: string; label: string; href: string }> = [
  { id: "terminal", label: "Terminal", href: "/" },
  { id: "portfolio", label: "Portfolio", href: "/portfolio" },
  { id: "markets", label: "Markets", href: "/markets" },
  { id: "screener", label: "Screener", href: "/screener" },
  { id: "chat", label: "Chat", href: "/chat" },
];

function isActive(pathname: string | null, href: string): boolean {
  if (!pathname) return href === "/";
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TerminalTopBar() {
  const router = useRouter();
  const pathname = usePathname();

  const nav: TopBarNavItem[] = NAV_ITEMS.map((n) => ({
    id: n.id,
    label: n.label,
    active: isActive(pathname, n.href),
    onClick: () => router.push(n.href),
  }));

  return (
    <TopBar
      brand={
        <>
          <div
            className="grid h-7 w-7 place-items-center border-[1.5px] border-[color:var(--accent)] font-mono font-bold text-[color:var(--accent)] shadow-[0_0_18px_var(--glow),inset_0_0_12px_var(--glow)]"
            style={{
              background:
                "radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--accent) 30%, transparent), transparent 60%)",
            }}
          >
            △F
          </div>
          <span className="font-bold uppercase tracking-[0.24em] text-[12px] text-[color:var(--accent)]">
            Alpha Forge
          </span>
        </>
      }
      nav={nav}
      right={
        <>
          <LiveDot label="LIVE · NSE" />
          <Kbd>⌘K</Kbd>
          <span>◉ ARPIT</span>
        </>
      }
    />
  );
}
