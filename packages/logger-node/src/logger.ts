/**
 * Core logger implementation.
 *
 * Env-var resolution order for every option:
 *   1. Explicit option passed to `createLogger()`
 *   2. Environment variable (LOG_LEVEL, LOG_DIR, LOG_FILE)
 *   3. Built-in default
 */

import pino from "pino";

const isServer = typeof window === "undefined";

// ── Types ───────────────────────────────────────────────────

export interface LoggerOptions {
  /** Root logger name (default: "alphaforge") */
  name?: string;
  /** Minimum log level (default: env LOG_LEVEL ?? "info") */
  level?: string;
  /** Directory for log files, relative to cwd (default: env LOG_DIR ?? "logs") */
  logDir?: string;
  /** Log filename (default: env LOG_FILE ?? "alphaforge.log") */
  logFile?: string;
  /** Use pino-pretty for console in dev (default: NODE_ENV !== "production") */
  pretty?: boolean;
}

// ── Singleton ───────────────────────────────────────────────

let _logger: pino.Logger | null = null;

/**
 * Create (or reconfigure) the singleton root logger.
 *
 * Call this once at application startup. Subsequent calls to `getLogger()`
 * return child loggers from this root.
 */
export function createLogger(opts: LoggerOptions = {}): pino.Logger {
  const name = opts.name ?? "alphaforge";
  const level = opts.level ?? (isServer ? process.env.LOG_LEVEL : undefined) ?? "info";

  if (isServer) {
    const fs = require("node:fs") as typeof import("node:fs");
    const path = require("node:path") as typeof import("node:path");

    const logDir = opts.logDir ?? process.env.LOG_DIR ?? "logs";
    const logFile = opts.logFile ?? process.env.LOG_FILE ?? "alphaforge.log";
    const logPath = path.resolve(process.cwd(), logDir, logFile);

    // Ensure log directory exists
    fs.mkdirSync(path.dirname(logPath), { recursive: true });

    const pretty = opts.pretty ?? process.env.NODE_ENV !== "production";

    const targets: pino.TransportTargetOptions[] = [
      // Console: pretty in dev, raw JSON in prod
      pretty
        ? {
            target: "pino-pretty",
            options: { colorize: true, translateTime: "SYS:yyyy-mm-dd HH:MM:ss" },
            level,
          }
        : {
            target: "pino/file",
            options: { destination: 1 }, // stdout
            level,
          },
      // Always write to file
      {
        target: "pino/file",
        options: { destination: logPath, mkdir: true },
        level,
      },
    ];

    _logger = pino(
      { level, name, timestamp: pino.stdTimeFunctions.isoTime },
      pino.transport({ targets }),
    );
  } else {
    // Client-side: browser console
    _logger = pino({
      level,
      name,
      browser: { asObject: true },
      timestamp: pino.stdTimeFunctions.isoTime,
    });
  }

  return _logger;
}

/**
 * Get a child logger scoped to a module/component.
 *
 * If `createLogger()` hasn't been called yet, a default logger is created
 * automatically (console-only on client, file+console on server).
 *
 * @example
 * ```ts
 * const log = getLogger("MarketOverview");
 * log.info("component mounted");
 * ```
 */
export function getLogger(module: string): pino.Logger {
  if (!_logger) {
    createLogger();
  }
  return _logger!.child({ module });
}
