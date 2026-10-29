"""Фикстуры API-клиентов и тестовых пользователей."""

from collections.abc import Iterator
from http import HTTPStatus

import pytest
from pydantic import BaseModel, EmailStr

from clients.private_http_builder import AuthenticationUserSchema
from clients.users.private_users_client import PrivateUsersClient, get_private_users_client
from clients.users.public_users_client import PublicUsersClient, get_public_users_client
from clients.users.user_schema import CreateUserRequestSchema, CreateUserResponseSchema, GetUserResponseSchema
from tools.assertions.base import assert_is_true, assert_status_code
from tools.assertions.schema import validate_json_schema
from tools.assertions.users import assert_create_user_response, assert_get_user_response
from tools.fakers import fake


class UserFixture(BaseModel):
    """Данные пользователя, созданного фикстурой.

    Attributes:
        request: Запрос на создание пользователя с его учетными данными.
        response: Ответ API с данными созданного пользователя.
    """

    request: CreateUserRequestSchema
    response: CreateUserResponseSchema

    @property
    def email(self) -> EmailStr:
        """Возвращает email пользователя.

        Returns:
            Email из запроса на создание пользователя.
        """
        return self.request.email

    @property
    def password(self) -> str:
        """Возвращает пароль пользователя.

        Returns:
            Пароль из запроса на создание пользователя.
        """
        return self.request.password

    @property
    def authentication_user(self) -> AuthenticationUserSchema:
        """Формирует учетные данные для авторизации API-клиентов.

        Returns:
            Модель с email и паролем созданного пользователя.
        """
        return AuthenticationUserSchema(email=self.email, password=self.password)


@pytest.fixture
def public_users_client() -> Iterator[PublicUsersClient]:
    """Создает публичный клиент пользователей для одного теста.

    Закрывает HTTP-соединения при завершении фикстуры.

    Yields:
        API-клиент для работы с публичными методами пользователей.
    """
    public_client = get_public_users_client()
    with public_client.client:
        yield public_client


@pytest.fixture
def function_user(public_users_client: PublicUsersClient) -> UserFixture:
    """Создает нового пользователя для одного теста.

    Args:
        public_users_client: Фикстура публичного API-клиента пользователей.

    Returns:
        Запрос и ответ создания пользователя, проверенный по полям запроса.

    Raises:
        AssertionError: Если данные созданного пользователя не соответствуют запросу.
    """
    request = CreateUserRequestSchema()
    response = public_users_client.create_user(request=request)
    assert_create_user_response(request=request, response=response)
    return UserFixture(request=request, response=response)


@pytest.fixture
def user_request_with_existing_email(function_user: UserFixture) -> CreateUserRequestSchema:
    """Готовит тот же email и отличающиеся пароль, имя, фамилию и отчество."""
    original = function_user.request
    return CreateUserRequestSchema(
        email=original.email,
        password=fake.password_different_from(original.password),
        first_name=fake.text_different_from(original.first_name),
        last_name=fake.text_different_from(original.last_name),
        middle_name=fake.text_different_from(original.middle_name),
    )


@pytest.fixture
def private_users_client(function_user: UserFixture) -> Iterator[PrivateUsersClient]:
    """Создает авторизованный клиент пользователей для одного теста.

    Использует учетные данные созданного пользователя и закрывает
    HTTP-соединения при завершении фикстуры.

    Args:
        function_user: Фикстура с данными созданного пользователя.

    Yields:
        API-клиент для работы с приватными методами пользователей.
    """
    private_client = get_private_users_client(user=function_user.authentication_user)
    with private_client.client:
        yield private_client


@pytest.fixture
def function_user_to_delete(
    public_users_client: PublicUsersClient,
    private_users_client: PrivateUsersClient,
    function_user: UserFixture,
) -> UserFixture:
    """Создаёт отдельную цель удаления и проверяет её через клиента наблюдателя.

    Сверяет данные обоих пользователей с входом и исключает совпадение ID.
    Само удаление выполняется в тесте.
    """
    create_user_request = CreateUserRequestSchema()
    create_user_response = public_users_client.create_user_api(request=create_user_request)
    assert_status_code(create_user_response.status_code, HTTPStatus.OK)
    validate_json_schema(create_user_response.json(), CreateUserResponseSchema.model_json_schema())
    create_user_response_data = CreateUserResponseSchema.model_validate_json(create_user_response.text)
    assert_create_user_response(request=create_user_request, response=create_user_response_data)
    target_id = create_user_response_data.user.id
    assert_is_true(target_id != function_user.response.user.id, name="separate user ID")
    get_user_response = private_users_client.get_user_api(user_id=target_id)
    assert_status_code(get_user_response.status_code, HTTPStatus.OK)
    validate_json_schema(get_user_response.json(), GetUserResponseSchema.model_json_schema())
    get_user_response_data = GetUserResponseSchema.model_validate_json(get_user_response.text)
    assert_get_user_response(get_user_response=get_user_response_data, create_user_response=create_user_response_data)
    return UserFixture(request=create_user_request, response=create_user_response_data)
