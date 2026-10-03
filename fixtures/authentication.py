"""Фикстуры API-клиентов аутентификации."""

from collections.abc import Iterator

import pytest

from clients.authentication.authentication_client import AuthenticationClient, get_authentication_client


@pytest.fixture
def authentication_client() -> Iterator[AuthenticationClient]:
    """Создает клиент аутентификации для одного теста.

    Закрывает HTTP-соединения при завершении фикстуры.

    Yields:
        API-клиент для работы с аутентификацией.
    """
    auth_client = get_authentication_client()
    with auth_client.client:
        yield auth_client
