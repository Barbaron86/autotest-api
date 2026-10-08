"""Фикстуры метаданных отчета Allure."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from tools.allure.environment import create_allure_environment_file


@pytest.fixture(scope="session", autouse=True)
def save_allure_environment_file(pytestconfig: pytest.Config) -> Iterator[None]:
    """Сохраняет сведения об окружении после завершения тестов.

    Args:
        pytestconfig: Конфигурация текущего запуска pytest.

    Yields:
        Управление тестам до записи файла environment.properties.
    """
    yield
    results_dir = pytestconfig.getoption("allure_report_dir")
    if results_dir:
        create_allure_environment_file(Path(results_dir))
