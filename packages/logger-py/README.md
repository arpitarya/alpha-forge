# alphaforge-logger

Structured rotating-file + console logger for AlphaForge Python services.

## Install

```bash
# As a local path dependency (monorepo)
pdm add ./packages/logger-py

# Or via pip
pip install alphaforge-logger
```

## Usage

```python
from alphaforge_logger import setup_logging, get_logger

# Call once at app startup
setup_logging(level="INFO", log_dir="logs", log_file="my-service.log")

# Get a scoped logger anywhere
logger = get_logger("routes.market")
logger.info("Quote requested for symbol=%s", symbol)
```

## Configuration

All parameters can be set via kwargs or environment variables:

| Kwarg | Env Var | Default | Description |
|-------|---------|---------|-------------|
| `level` | `LOG_LEVEL` | `INFO` | Minimum log level |
| `log_dir` | `LOG_DIR` | `logs` | Directory for log files |
| `log_file` | `LOG_FILE` | `alphaforge.log` | Log filename |
| `max_bytes` | `LOG_MAX_BYTES` | `10485760` (10 MB) | Max file size before rotation |
| `backup_count` | `LOG_BACKUP_COUNT` | `5` | Rotated backup files to keep |
