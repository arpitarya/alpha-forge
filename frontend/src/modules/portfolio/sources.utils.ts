import type { SourceInfoDTO } from "./portfolio.types";

export const OTP_SLUGS = new Set(["wint-wealth"]);

export function formatTime(iso: string | null): string {
  if (!iso) return "never";
  const dt = new Date(iso);
  const diffMs = Date.now() - dt.getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hrs = Math.floor(min / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function statusVariant(status: SourceInfoDTO["status"]) {
  switch (status) {
    case "ready":
      return "success" as const;
    case "syncing":
      return "warning" as const;
    case "error":
      return "danger" as const;
    default:
      return "default" as const;
  }
}

export function readErr(e: unknown): string {
  const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  return detail ?? (e as Error).message;
}
