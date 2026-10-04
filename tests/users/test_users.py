from http import HTTPStatus

import pytest

from clients.users.private_users_client import PrivateUsersClient
from clients.users.public_users_client import PublicUsersClient
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema, GetUserResponseSchema
from fixtures.users import UserFixture
from tools.assertions.base import assert_status_code
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import assert_create_user_response, assert_get_user_response
from tools.fakers import fake


@pytest.mark.users
@pytest.mark.regression
class TestUsers:
    @pytest.mark.parametrize("email", ["mail.ru", "gmail.com", "example.com"])
    def test_create_user(self, email: str, public_users_client: PublicUsersClient) -> None:
        """Проверяет создание пользователя с email на заданном домене.

        Создает пользователя со сгенерированными данными и проверяет
        HTTP-статус, данные пользователя и JSON Schema ответа.

        Args:
            email: Домен для генерации случайного email-адреса.
            public_users_client: Фикстура публичного API-клиента пользователей.

        Raises:
            AssertionError: Если HTTP-статус или данные пользователя
                не соответствуют ожиданиям.
        """
        request = CreateUserRequestSchema(email=fake.email(domain=email))
        response = public_users_client.create_user_api(request=request)

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)
        response_data = CreateUserResponseSchema.model_validate_json(response.text)
        assert_create_user_response(request=request, response=response_data)

        validate_json_schema(response.json(), response_data.model_json_schema())

    def test_get_user_me(self, private_users_client: PrivateUsersClient, function_user: UserFixture) -> None:
        """Проверяет получение данных текущего пользователя.

        Запрашивает данные авторизованного пользователя и проверяет
        HTTP-статус, совпадение данных с ответом на создание и JSON Schema.

        Args:
            private_users_client: Фикстура авторизованного API-клиента пользователей.
            function_user: Фикстура с данными созданного пользователя.

        Raises:
            AssertionError: Если HTTP-статус или данные пользователя
                не соответствуют ожиданиям.
        """
        response = private_users_client.get_user_me_api()

        assert_status_code(actual=response.status_code, expected=HTTPStatus.OK)
        response_data = GetUserResponseSchema.model_validate_json(response.text)
        assert_get_user_response(get_user_response=response_data, create_user_response=function_user.response)

        validate_json_schema(instance=response.json(), schema=GetUserResponseSchema.model_json_schema())
