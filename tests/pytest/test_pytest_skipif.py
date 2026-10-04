"""Учебные примеры пропуска тестов по версии системы из урока 8.4."""

import pytest

SYSTEM_VERSION = "v1.2.0"


@pytest.mark.skipif(
    SYSTEM_VERSION == "v1.3.0",
    reason="Тест не может быть запущен на версии системы v1.3.0",
)
def test_system_version_valid() -> None:
    pass


@pytest.mark.skipif(
    SYSTEM_VERSION == "v1.2.0",
    reason="Тест не может быть запущен на версии системы v1.2.0",
)
def test_system_version_invalid() -> None:
    pass
