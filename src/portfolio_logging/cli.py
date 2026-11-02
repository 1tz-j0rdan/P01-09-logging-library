"""CLI demo for the reusable logging library."""

import argparse

from .core import configure_logger


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a test log message")
    parser.add_argument("message", help="Message to log")
    parser.add_argument(
    "--level",
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
    parser.add_argument("--file", help="Optional rotating log file")
    parser.add_argument("--json", action="store_true", help="Emit JSON lines")
    parser.add_argument("--no-console", action="store_true", help="Write only to file")
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--backups", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        logger = configure_logger(
            level=args.level,
            console=not args.no_console,
            file=args.file,
            json_format=args.json,
            max_bytes=args.max_bytes,
            backup_count=args.backups,
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    logger.log(logger.level, args.message)
    return 0
