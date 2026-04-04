# @alphaforge/logger

Structured pino logger with file + console output for AlphaForge Node/TypeScript services.

## Install

```bash
# Workspace dependency (monorepo)
pnpm add @alphaforge/logger

# With pretty printing in dev
pnpm add -D pino-pretty
```

## Usage

```ts
import { createLogger, getLogger } from "@alphaforge/logger";

// Call once at app startup (creates file transport on server)
createLogger({
  name: "my-service",
  logFile: "my-service.log",
});

// Get a scoped logger anywhere
const log = getLogger("MarketOverview");
log.info("component mounted");
log.error({ err }, "failed to fetch quotes");
```

## Configuration

All options can be set via `createLogger()` opts or environment variables:

| Option | Env Var | Default | Description |
|--------|---------|---------|-------------|
| `level` | `LOG_LEVEL` | `info` | Minimum log level |
| `logDir` | `LOG_DIR` | `logs` | Directory for log files |
| `logFile` | `LOG_FILE` | `alphaforge.log` | Log filename |
| `name` | — | `alphaforge` | Root logger name |
| `pretty` | — | `NODE_ENV !== "production"` | Pretty-print console output |

## Environments

- **Server (Node.js)**: Logs to stdout + `{logDir}/{logFile}` via pino transports
- **Client (Browser)**: Logs to console via pino browser binding
