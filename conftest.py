"""Подключение модулей фикстур как плагинов pytest."""

pytest_plugins = (
    "fixtures.allure",
    "fixtures.users",
    "fixtures.authentication",
    "fixtures.files",
    "fixtures.courses",
    "fixtures.exercises",
)
