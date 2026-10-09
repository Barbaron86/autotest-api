"""Подключение модулей фикстур как плагинов pytest."""

from tools.logger import configure_logging

pytest_plugins = (
    "fixtures.allure",
    "fixtures.users",
    "fixtures.authentication",
    "fixtures.files",
    "fixtures.courses",
    "fixtures.exercises",
)


def pytest_configure() -> None:
    """Настраивает консольные логи в контроллере pytest и каждом worker."""
    configure_logging()
