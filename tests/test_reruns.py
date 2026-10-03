"""Учебные примеры перезапусков автотестов из урока 8.8."""

import random

import pytest

PLATFORM = "Linux"


@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_reruns() -> None:
    """Демонстрирует перезапуски нестабильного теста на уровне функции.

    Raises:
        AssertionError: Если случайно выбрано значение False.
    """
    assert random.choice([True, False])


@pytest.mark.flaky(reruns=3, reruns_delay=2)
class TestReruns:
    """Демонстрирует применение перезапусков ко всем тестам класса."""

    def test_rerun_1(self) -> None:
        """Демонстрирует перезапуски первого нестабильного теста класса.

        Raises:
            AssertionError: Если случайно выбрано значение False.
        """
        assert random.choice([True, False])

    def test_rerun_2(self) -> None:
        """Демонстрирует перезапуски второго нестабильного теста класса.

        Raises:
            AssertionError: Если случайно выбрано значение False.
        """
        assert random.choice([True, False])


@pytest.mark.flaky(reruns=3, reruns_delay=2, condition=PLATFORM == "Windows")
def test_rerun_with_condition() -> None:
    """Демонстрирует перезапуски только при выполнении условия.

    В учебном примере PLATFORM равен Linux, поэтому перезапусков нет.

    Raises:
        AssertionError: Если случайно выбрано значение False.
    """
    assert random.choice([True, False])
