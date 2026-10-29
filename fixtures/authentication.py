"""Фикстуры клиентов и пользователей для проверки аутентификации."""

from collections.abc import Iterator
from http import HTTPStatus

import pytest

from clients.authentication.authentication_client import AuthenticationClient, get_authentication_client
from clients.authentication.authentication_schema import LoginRequestSchema, LoginResponseSchema
from fixtures.users import UserFixture
from tools.assertions.authentication import assert_login_response
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema


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


@pytest.fixture
def function_user_with_verified_credentials(
    function_user: UserFixture,
    authentication_client: AuthenticationClient,
) -> UserFixture:
    """Возвращает пользователя после проверки входа с правильным паролем.

    Args:
        function_user: Фикстура с данными созданного пользователя.
        authentication_client: Фикстура API-клиента аутентификации.

    Returns:
        Исходный пользователь с проверенными учетными данными для входа.

    Raises:
        AssertionError: Если HTTP-статус, структура ответа или токены
            не соответствуют успешному входу.
    """
    login_request = LoginRequestSchema(email=function_user.email, password=function_user.password)
    login_response = authentication_client.login_api(request=login_request)

    assert_status_code(actual=login_response.status_code, expected=HTTPStatus.OK)
    validate_json_schema(instance=login_response.json(), schema=LoginResponseSchema.model_json_schema())

    login_response_data = LoginResponseSchema.model_validate_json(login_response.text)
    assert_login_response(response=login_response_data)

    return function_user
