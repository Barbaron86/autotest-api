"""Настройка стандартного логирования автотестов."""

import logging


def get_logger(name: str) -> logging.Logger:
    """Создает именованный логгер с выводом в консоль.

    Args:
        name: Имя компонента, сообщения которого записывает логгер.

    Returns:
        Логгер с уровнем DEBUG и единым форматом сообщений.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
        logger.addHandler(handler)

    return logger
