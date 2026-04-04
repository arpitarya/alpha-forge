/**
 * @alphaforge/logger — Structured pino logger with file + console output.
 *
 * Works on both server (Node.js) and client (browser) environments.
 *
 * Server-side: logs to stdout + rotating log file via pino transports.
 * Client-side: logs to console via pino browser binding.
 *
 * @example
 * ```ts
 * import { createLogger, getLogger } from "@alphaforge/logger";
 *
 * // Call once at app bootstrap (server only — creates file transport)
 * createLogger({ name: "my-service", logFile: "my-service.log" });
 *
 * // Then anywhere in the codebase
 * const log = getLogger("MarketOverview");
 * log.info("component mounted");
 * ```
 */

export { createLogger, getLogger } from "./logger.js";
export type { LoggerOptions } from "./logger.js";
