# P01-09 — Logging Library

Reusable Python logging library with configurable log levels, console output, rotating files, and structured JSON lines. Uses the Python standard library; no runtime dependencies.

## Install (PowerShell)

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Try it

```powershell
python -m portfolio_logging "Application started"
python -m portfolio_logging "User signed in" --level INFO --json
New-Item -ItemType Directory -Force .\demo-files
python -m portfolio_logging "File logging works" --file .\demo-files\app.log --no-console
Get-Content .\demo-files\app.log
python -m portfolio_logging "Structured event" --file .\demo-files\events.log --json --no-console
Get-Content .\demo-files\events.log
```

## Use as a Python library

```python
from portfolio_logging import configure_logger

logger = configure_logger(
    "myapp",
    level="DEBUG",
    file="logs/app.log",
    json_format=True,
    max_bytes=100_000,
    backup_count=3,
)
logger.info("Application started")
logger.warning("Low disk space")
```

`configure_logger` returns a named `logging.Logger` and replaces previously attached handlers on that logger. It sets `propagate=False` to avoid duplicate messages from the root logger. JSON records contain UTC timestamp, level, logger, and message; exceptions include an exception field. File rotation uses `RotatingFileHandler`.

## Validate

```powershell
python -m pytest -v
python -m ruff check .
```

## Structure

- `src/portfolio_logging/core.py`: configuration and JSON formatter
- `src/portfolio_logging/cli.py`: demonstration CLI
- `tests/test_core.py`: automated tests
- `.github/workflows/ci.yml`: GitHub Actions checks

## Notes

- Log files and `demo-files/` are ignored by Git.
- Do not log passwords, tokens, or sensitive personal data.
- Rotation is based on file size, not time. For multiple processes writing the same file, use a centralized logging system.
