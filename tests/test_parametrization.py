"""Учебные примеры параметризации pytest из урока 8.7."""

from typing import cast

import pytest
from _pytest.fixtures import SubRequest


@pytest.mark.parametrize("number", [1, 2, 3, -1])
def test_numbers(number: int) -> None:
    """Демонстрирует запуск теста для каждого значения параметра.

    Случай с -1 намеренно завершается ошибкой, как в примере курса.

    Args:
        number: Число для проверки.

    Raises:
        AssertionError: Если число не положительное.
    """
    assert number > 0


@pytest.mark.parametrize("number, expected", [(1, 1), (2, 4), (3, 9)])
def test_several_numbers(number: int, expected: int) -> None:
    """Демонстрирует передачу нескольких параметров в один тест.

    Args:
        number: Число для возведения в квадрат.
        expected: Ожидаемый квадрат числа.

    Raises:
        AssertionError: Если квадрат числа не совпадает с ожидаемым.
    """
    assert number**2 == expected


@pytest.mark.parametrize("os", ["macos", "windows", "linux", "debian"])
@pytest.mark.parametrize("host", ["https://dev.company.com", "https://stable.company.com", "https://prod.company.com"])
def test_multiplication_of_numbers(os: str, host: str) -> None:
    """Демонстрирует декартово произведение двух наборов параметров.

    Args:
        os: Название операционной системы.
        host: Адрес хоста из учебного примера.

    Raises:
        AssertionError: Если объединенная строка параметров пустая.
    """
    assert len(os + host) > 0


@pytest.fixture(params=["https://dev.company.com", "https://stable.company.com", "https://prod.company.com"])
def host(request: SubRequest) -> str:
    """Возвращает один из хостов через параметризацию фикстуры.

    Args:
        request: Запрос pytest с текущим значением параметра фикстуры.

    Returns:
        Адрес хоста для текущего запуска теста.
    """
    return cast(str, request.param)


def test_host(host: str) -> None:
    """Демонстрирует параметризацию теста через фикстуру.

    Args:
        host: Адрес хоста, возвращенный параметризованной фикстурой.
    """
    print(f"Running test on host: {host}")


@pytest.mark.parametrize("user", ["Alice", "Zara"])
class TestOperations:
    """Демонстрирует параметризацию всех тестовых методов класса."""

    def test_user_with_operations(self, user: str) -> None:
        """Выводит пользователя из учебного сценария с операциями.

        Args:
            user: Имя пользователя из параметризации класса.
        """
        print(f"User with operations: {user}")

    def test_user_without_operations(self, user: str) -> None:
        """Выводит пользователя из учебного сценария без операций.

        Args:
            user: Имя пользователя из параметризации класса.
        """
        print(f"User without operations: {user}")


users = {
    "+70000000011": "User with money on bank account",
    "+70000000022": "User without money on bank account",
    "+70000000033": "User with operations on bank account",
}


@pytest.mark.parametrize(
    "phone_number", users.keys(), ids=lambda phone_number: f"{phone_number}: {users[phone_number]}"
)
def test_identifiers(phone_number: str) -> None:
    """Демонстрирует динамические идентификаторы параметров.

    Args:
        phone_number: Номер телефона пользователя из учебного словаря.
    """
    pass
