/**
 * POST /api/log — Receives client-side log entries and writes them to the
 * server log file via pino. Only accepts "warn", "error", and "fatal" levels.
 */

import { type NextRequest, NextResponse } from "next/server";
import { getLogger } from "@alphaforge/logger";

const logger = getLogger("client-log-relay");

const ALLOWED_LEVELS = new Set(["warn", "error", "fatal"]);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { level, message, module, ...extra } = body as {
      level: string;
      message: string;
      module?: string;
      [key: string]: unknown;
    };

    if (!level || !message) {
      return NextResponse.json({ error: "level and message are required" }, { status: 400 });
    }

    if (!ALLOWED_LEVELS.has(level)) {
      return NextResponse.json({ error: "level must be warn, error, or fatal" }, { status: 400 });
    }

    const child = module
      ? logger.child({ module, source: "client" })
      : logger.child({ source: "client" });
    child[level as "warn" | "error" | "fatal"](extra, message);

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "invalid request body" }, { status: 400 });
  }
}
