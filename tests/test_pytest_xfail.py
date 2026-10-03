"""Учебные примеры ожидаемого падения и неожиданного успеха из урока 8.4."""

import pytest


@pytest.mark.xfail(reason="Найден баг в приложении, из-за которого тест падает с ошибкой")
def test_with_bug() -> None:
    assert 1 == 2  # type: ignore[comparison-overlap]  # Заведомое падение для примера XFAIL.


@pytest.mark.xfail(reason="Баг уже исправлен, но на тест все еще висит маркировка xfail")
def test_without_bug() -> None:
    pass


@pytest.mark.xfail(reason="Внешний сервис временно недоступен")
def test_external_services_is_unavailable() -> None:
    assert 1 == 2  # type: ignore[comparison-overlap]  # Заведомое падение для примера XFAIL.
