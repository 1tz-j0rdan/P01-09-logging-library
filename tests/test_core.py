import json
import logging
from pathlib import Path

import pytest

from portfolio_logging import configure_logger, get_logger
from portfolio_logging.cli import main


@pytest.fixture
def logger_name(request):
    return f"portfolio.test.{request.node.name}"


def test_console_output(capsys, logger_name):
    logger = configure_logger(logger_name)
    logger.info("hello")
    assert "hello" in capsys.readouterr().out


def test_level_filter(capsys, logger_name):
    logger = configure_logger(logger_name, level="WARNING")
    logger.info("hidden")
    logger.warning("visible")
    output = capsys.readouterr().out
    assert "visible" in output
    assert "hidden" not in output


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_valid_levels(level, logger_name):
    assert configure_logger(logger_name, level=level).level == logging.getLevelName(level)


@pytest.mark.parametrize("level", ["TRACE", "", "NOTSET", "infoo"])
def test_invalid_levels(level, logger_name):
    with pytest.raises(ValueError):
        configure_logger(logger_name, level=level)


def test_empty_name():
    with pytest.raises(ValueError):
        configure_logger("")


def test_file_output(tmp_path, logger_name):
    destination = tmp_path / "nested" / "app.log"
    logger = configure_logger(logger_name, console=False, file=destination)
    logger.error("file message")
    assert "file message" in destination.read_text(encoding="utf-8")


def test_json_output(tmp_path, logger_name):
    destination = tmp_path / "events.log"
    logger = configure_logger(logger_name, console=False, file=destination, json_format=True)
    logger.info("a message")
    payload = json.loads(destination.read_text(encoding="utf-8").strip())
    assert payload["level"] == "INFO"
    assert payload["message"] == "a message"
    assert payload["logger"] == logger_name
    assert payload["timestamp"].endswith("+00:00")


def test_json_unicode(tmp_path, logger_name):
    destination = tmp_path / "unicode.log"
    logger = configure_logger(logger_name, console=False, file=destination, json_format=True)
    logger.info("café")
    assert "café" in destination.read_text(encoding="utf-8")


def test_json_exception(tmp_path, logger_name):
    destination = tmp_path / "errors.log"
    logger = configure_logger(logger_name, console=False, file=destination, json_format=True)
    try:
        raise RuntimeError("broken")
    except RuntimeError:
        logger.exception("operation failed")
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert "RuntimeError: broken" in payload["exception"]


def test_rotation(tmp_path, logger_name):
    destination = tmp_path / "rotate.log"
    logger = configure_logger(
        logger_name, console=False, file=destination, max_bytes=100, backup_count=2
    )
    for index in range(20):
        logger.info("message %s %s", index, "x" * 40)
    assert destination.exists()
    assert Path(f"{destination}.1").exists()
    assert len(list(tmp_path.glob("rotate.log*"))) <= 3


def test_no_duplicate_handlers(logger_name):
    configure_logger(logger_name)
    configure_logger(logger_name)
    assert len(get_logger(logger_name).handlers) == 1


def test_get_logger(logger_name):
    configured = configure_logger(logger_name)
    assert get_logger(logger_name) is configured


def test_no_outputs(logger_name):
    with pytest.raises(ValueError):
        configure_logger(logger_name, console=False)


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_invalid_max_bytes(value, logger_name):
    with pytest.raises(ValueError):
        configure_logger(logger_name, max_bytes=value)


@pytest.mark.parametrize("value", [-1, True, 1.5])
def test_invalid_backups(value, logger_name):
    with pytest.raises(ValueError):
        configure_logger(logger_name, backup_count=value)


def test_cli_console(capsys):
    assert main(["hello from cli"]) == 0
    assert "hello from cli" in capsys.readouterr().out


def test_cli_file(tmp_path):
    destination = tmp_path / "cli.log"
    assert main(["from cli", "--file", str(destination), "--no-console", "--json"]) == 0
    assert json.loads(destination.read_text(encoding="utf-8"))["message"] == "from cli"


def test_cli_missing_destination():
    with pytest.raises(SystemExit) as exc:
        main(["message", "--no-console"])
    assert exc.value.code == 2
