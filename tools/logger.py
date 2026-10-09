"""Единая настройка консольных логов автотестов."""

import os
import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import BasicHandlerConfig, Message


def _write_to_stderr(message: "Message") -> None:
    """Пишет сообщение в текущий stderr с учётом захвата вывода pytest.

    Args:
        message: Отформатированное сообщение Loguru.
    """
    sys.stderr.write(message)
    sys.stderr.flush()


def configure_logging() -> None:
    """Настраивает один консольный sink для текущего процесса pytest.

    Уровень задаётся через LOGURU_LEVEL и по умолчанию равен INFO.
    LOGURU_COLORIZE управляет цветом; без неё цвет включается для TTY.
    Повторный вызов заменяет предыдущие sinks без дублирования сообщений.
    """
    handler: BasicHandlerConfig = {
        "sink": _write_to_stderr,
        "level": os.getenv("LOGURU_LEVEL", "INFO"),
        "format": (
            "<dim>{time:HH:mm:ss.SSS}</dim> | <dim>{extra[worker]}</dim> | "
            "<level>{level: <7}</level> | <cyan>{name}</cyan> | {message}"
        ),
        "diagnose": False,
        "backtrace": False,
        "enqueue": False,
    }
    if "LOGURU_COLORIZE" not in os.environ:
        handler["colorize"] = sys.stderr.isatty()

    logger.configure(
        handlers=[handler],
        extra={"worker": os.getenv("PYTEST_XDIST_WORKER", "main")},
    )
