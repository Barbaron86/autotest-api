"""Подключение модулей фикстур как плагинов pytest."""

pytest_plugins = (
    "fixtures.users",
    "fixtures.authentication",
)
