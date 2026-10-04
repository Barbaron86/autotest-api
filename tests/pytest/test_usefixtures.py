"""Учебные примеры подключения фикстур через usefixtures из урока 8.5."""

import pytest


@pytest.fixture
def clear_books_database() -> None:
    """Демонстрирует подготовку окружения перед тестом.

    Выводит учебное сообщение об очистке базы данных.
    """
    print("[FIXTURE] Удаляем все данные из базы данных")


@pytest.fixture
def fill_books_database() -> None:
    """Демонстрирует заполнение тестовых данных перед тестом.

    Выводит учебное сообщение о добавлении книг в базу данных.
    """
    print("[FIXTURE] Создаем новые данные в базе данных")


@pytest.mark.usefixtures("fill_books_database")
def test_read_all_books_in_library() -> None:
    """Подключает фикстуру заполнения базы данных через usefixtures."""
    pass


@pytest.mark.usefixtures("clear_books_database", "fill_books_database")
class TestLibrary:
    """Учебные сценарии применения usefixtures ко всему тестовому классу."""

    def test_read_book_from_library(self) -> None:
        """Подключает фикстуры очистки и заполнения данных перед чтением книги."""
        pass

    def test_delete_book_from_library(self) -> None:
        """Подключает фикстуры очистки и заполнения данных перед удалением книги."""
        pass
