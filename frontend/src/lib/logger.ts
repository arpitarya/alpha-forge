/**
 * AlphaForge Frontend — Logger (thin wrapper around @alphaforge/logger).
 *
 * Initialises the shared logger package with frontend-specific defaults.
 * Server-side: logs to stdout + file.  Client-side: logs to console.
 *
 * Configured via env vars: LOG_LEVEL, LOG_DIR, LOG_FILE
 */

import { createLogger, getLogger as _getLogger } from "../../../packages/logger-node/dist";

const logger = createLogger({
  name: "alphaforge-frontend",
  logFile: process.env.LOG_FILE ?? "alphaforge-frontend.log",
});

/**
 * Get a child logger scoped to a module/component.
 * Usage: `const log = getLogger("MarketOverview");`
 */
export function getLogger(module: string) {
  return _getLogger(module);
}

export default logger;
